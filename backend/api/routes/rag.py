"""
RAG API Routes
Endpoints for document ingestion and RAG-based chat
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import os
import shutil
from pathlib import Path
import logging

# Import RAG pipeline
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from rag.pipeline import RAGPipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rag", tags=["rag"])

# Initialize global RAG pipeline
rag_pipeline: Optional[RAGPipeline] = None


def get_rag_pipeline() -> RAGPipeline:
    """Get or create RAG pipeline instance"""
    global rag_pipeline

    if rag_pipeline is None:
        # Determine embedding provider from environment
        embedding_provider = os.getenv("EMBEDDING_PROVIDER", "huggingface")
        embedding_model = os.getenv("EMBEDDING_MODEL")

        rag_pipeline = RAGPipeline(
            embedding_provider=embedding_provider,
            embedding_model=embedding_model,
            chunk_size=int(os.getenv("CHUNK_SIZE", "1000")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "200")),
            persist_dir=os.getenv("VECTOR_STORE_DIR", "data/vectorstore")
        )

        # Try to load existing vectorstore
        rag_pipeline.load_existing()

    return rag_pipeline


# Request/Response models
class QueryRequest(BaseModel):
    question: str = Field(..., description="User question")
    k: int = Field(4, description="Number of documents to retrieve", ge=1, le=10)
    model: str = Field("gpt-3.5-turbo", description="LLM model to use")


class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: List[Dict]
    num_sources: int


class IngestRequest(BaseModel):
    directory_path: str = Field(..., description="Path to documents directory")
    file_types: Optional[List[str]] = Field(None, description="File types to process")


class IngestResponse(BaseModel):
    status: str
    documents_loaded: int
    chunks_created: int
    avg_chunk_size: float
    vectorstore_total_vectors: int


class StatusResponse(BaseModel):
    is_initialized: bool
    vectorstore_stats: Dict


# API Endpoints

@router.post("/chat/query", response_model=QueryResponse)
async def chat_query(request: QueryRequest, pipeline: RAGPipeline = Depends(get_rag_pipeline)):
    """
    Query the RAG system with a question

    Returns contextual answer with sources
    """
    try:
        logger.info(f"Received query: {request.question}")

        result = pipeline.chat(
            question=request.question,
            k=request.k,
            model=request.model
        )

        return QueryResponse(**result)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.post("/ingest/upload", response_model=IngestResponse)
async def ingest_upload(
    file: UploadFile = File(...),
    pipeline: RAGPipeline = Depends(get_rag_pipeline)
):
    """
    Upload and ingest a single document (PDF, TXT, MD)

    The document will be processed and added to the vector store
    """
    try:
        # Validate file type
        allowed_extensions = ['.pdf', '.txt', '.md']
        file_ext = Path(file.filename).suffix.lower()

        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {allowed_extensions}"
            )

        # Save uploaded file
        upload_dir = Path("data/documents/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)

        file_path = upload_dir / file.filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"Saved uploaded file: {file_path}")

        # Ingest document
        stats = pipeline.ingest_documents(str(file_path))

        return IngestResponse(**stats)

    except Exception as e:
        logger.error(f"Error ingesting file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error ingesting file: {str(e)}")


@router.post("/ingest/directory", response_model=IngestResponse)
async def ingest_directory(
    request: IngestRequest,
    pipeline: RAGPipeline = Depends(get_rag_pipeline)
):
    """
    Ingest all documents from a directory

    Processes all PDF, TXT, and MD files in the specified directory
    """
    try:
        directory = Path(request.directory_path)

        if not directory.exists():
            raise HTTPException(status_code=404, detail="Directory not found")

        if not directory.is_dir():
            raise HTTPException(status_code=400, detail="Path is not a directory")

        logger.info(f"Ingesting directory: {directory}")

        stats = pipeline.ingest_documents(
            str(directory),
            file_types=request.file_types
        )

        return IngestResponse(**stats)

    except Exception as e:
        logger.error(f"Error ingesting directory: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/status", response_model=StatusResponse)
async def get_status(pipeline: RAGPipeline = Depends(get_rag_pipeline)):
    """
    Get RAG system status

    Returns initialization status and vectorstore statistics
    """
    try:
        stats = pipeline.vectorstore.get_stats()

        return StatusResponse(
            is_initialized=pipeline.is_initialized,
            vectorstore_stats=stats
        )

    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.delete("/reset")
async def reset_vectorstore(pipeline: RAGPipeline = Depends(get_rag_pipeline)):
    """
    Reset the vector store

    WARNING: This will delete all ingested documents and embeddings
    """
    try:
        pipeline.reset()

        return {"status": "success", "message": "Vector store reset successfully"}

    except Exception as e:
        logger.error(f"Error resetting vectorstore: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/ingest/batch-upload")
async def ingest_batch_upload(
    files: List[UploadFile] = File(...),
    pipeline: RAGPipeline = Depends(get_rag_pipeline)
):
    """
    Upload and ingest multiple documents at once

    All files will be processed and added to the vector store
    """
    try:
        upload_dir = Path("data/documents/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)

        uploaded_files = []
        allowed_extensions = ['.pdf', '.txt', '.md']

        # Save all uploaded files
        for file in files:
            file_ext = Path(file.filename).suffix.lower()

            if file_ext not in allowed_extensions:
                logger.warning(f"Skipping unsupported file: {file.filename}")
                continue

            file_path = upload_dir / file.filename

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            uploaded_files.append(str(file_path))
            logger.info(f"Saved: {file_path}")

        if not uploaded_files:
            raise HTTPException(status_code=400, detail="No valid files uploaded")

        # Ingest all files from upload directory
        stats = pipeline.ingest_documents(str(upload_dir))

        return {
            "status": "success",
            "files_uploaded": len(uploaded_files),
            "ingestion_stats": stats
        }

    except Exception as e:
        logger.error(f"Error in batch upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
