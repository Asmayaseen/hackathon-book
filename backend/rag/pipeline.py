"""
RAG Pipeline Orchestrator
Coordinates the entire RAG workflow from ingestion to retrieval
"""
from typing import List, Optional, Dict
from pathlib import Path
import logging

from langchain.schema import Document

# Import RAG components (will be relative imports in actual deployment)
import sys
sys.path.append(str(Path(__file__).parent.parent))

from rag.ingestion.document_loader import DocumentLoader
from rag.chunking.text_splitter import DocumentChunker
from rag.embeddings.embedding_generator import EmbeddingGenerator
from rag.vectordb.faiss_store import FAISSVectorStore
from rag.retrieval.retriever import HybridRetriever, ContextualCompressor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGPipeline:
    """Complete RAG pipeline for document processing and retrieval"""

    def __init__(
        self,
        embedding_provider: str = "openai",
        embedding_model: Optional[str] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        persist_dir: str = "data/vectorstore"
    ):
        """
        Initialize RAG pipeline

        Args:
            embedding_provider: "openai" or "huggingface"
            embedding_model: Specific embedding model to use
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            persist_dir: Directory for vector store persistence
        """
        # Initialize components
        self.loader = DocumentLoader()
        self.chunker = DocumentChunker(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        self.embedding_generator = EmbeddingGenerator(
            provider=embedding_provider,
            model_name=embedding_model
        )

        self.vectorstore = FAISSVectorStore(
            embeddings=self.embedding_generator.embeddings,
            persist_directory=persist_dir
        )

        self.retriever: Optional[HybridRetriever] = None
        self.compressor = ContextualCompressor(max_tokens=500)

        self.is_initialized = False

        logger.info("RAG Pipeline initialized")

    def ingest_documents(
        self,
        source_path: str,
        file_types: Optional[List[str]] = None
    ) -> Dict:
        """
        Ingest documents from a directory or file

        Args:
            source_path: Path to document(s)
            file_types: List of file extensions to process

        Returns:
            Dictionary with ingestion statistics
        """
        logger.info(f"Starting document ingestion from {source_path}")

        # Step 1: Load documents
        source = Path(source_path)

        if source.is_dir():
            documents = self.loader.load_directory(str(source), file_types)
        elif source.suffix == '.pdf':
            documents = self.loader.load_pdf(str(source))
        elif source.suffix in ['.txt', '.md']:
            documents = self.loader.load_text(str(source))
        else:
            raise ValueError(f"Unsupported file type: {source.suffix}")

        # Step 2: Chunk documents
        chunks = self.chunker.chunk_documents(documents)

        # Step 3: Create/update vector store
        if self.vectorstore.vectorstore is None:
            self.vectorstore.create_from_documents(chunks)
        else:
            self.vectorstore.add_documents(chunks)

        # Step 4: Save vectorstore
        self.vectorstore.save()

        # Step 5: Initialize retriever
        self.retriever = HybridRetriever(self.vectorstore.vectorstore)
        self.retriever.index_documents_for_bm25(chunks)

        self.is_initialized = True

        # Get statistics
        chunk_stats = self.chunker.get_chunk_stats(chunks)
        vector_stats = self.vectorstore.get_stats()

        stats = {
            "source": str(source_path),
            "documents_loaded": len(documents),
            "chunks_created": len(chunks),
            "avg_chunk_size": chunk_stats.get("avg_chunk_size", 0),
            "vectorstore_total_vectors": vector_stats.get("total_vectors", 0),
            "status": "success"
        }

        logger.info(f"Ingestion complete: {stats}")
        return stats

    def query(
        self,
        question: str,
        k: int = 4,
        use_hybrid: bool = True,
        compress: bool = True
    ) -> Dict:
        """
        Query the RAG system

        Args:
            question: User question
            k: Number of documents to retrieve
            use_hybrid: Use hybrid search (vector + BM25)
            compress: Compress results to relevant parts only

        Returns:
            Dictionary with retrieved documents and metadata
        """
        if not self.is_initialized:
            raise ValueError("Pipeline not initialized. Ingest documents first.")

        logger.info(f"Processing query: {question}")

        # Retrieve documents
        retrieved_docs = self.retriever.retrieve(
            query=question,
            k=k,
            use_hybrid=use_hybrid,
            rerank=True
        )

        # Optionally compress
        if compress:
            retrieved_docs = self.compressor.compress(question, retrieved_docs)

        # Format response
        result = {
            "query": question,
            "num_results": len(retrieved_docs),
            "documents": [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "source": doc.metadata.get("source", "unknown")
                }
                for doc in retrieved_docs
            ]
        }

        logger.info(f"Retrieved {len(retrieved_docs)} documents")
        return result

    def generate_answer(
        self,
        question: str,
        context_docs: List[Document],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7
    ) -> str:
        """
        Generate answer using LLM with retrieved context

        Args:
            question: User question
            context_docs: Retrieved context documents
            model: LLM model to use
            temperature: Generation temperature

        Returns:
            Generated answer
        """
        from openai import OpenAI
        import os

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Build context from documents
        context = "\n\n".join([
            f"Document {i+1} (from {doc.metadata.get('source', 'unknown')}):\n{doc.page_content}"
            for i, doc in enumerate(context_docs)
        ])

        # Create prompt
        system_prompt = """You are a helpful AI assistant for the Physical AI & Humanoid Robotics course.
Answer questions based on the provided context. If the answer is not in the context, say so."""

        user_prompt = f"""Context:\n{context}\n\nQuestion: {question}\n\nAnswer based on the context above:"""

        # Generate response
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature
            )

            answer = response.choices[0].message.content
            logger.info("Generated answer successfully")
            return answer

        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            raise

    def chat(
        self,
        question: str,
        k: int = 4,
        model: str = "gpt-3.5-turbo"
    ) -> Dict:
        """
        Complete RAG chat: retrieve + generate answer

        Args:
            question: User question
            k: Number of documents to retrieve
            model: LLM model for generation

        Returns:
            Dictionary with answer and sources
        """
        # Retrieve relevant documents
        retrieval_result = self.query(question, k=k)
        context_docs = [
            Document(page_content=doc["content"], metadata=doc["metadata"])
            for doc in retrieval_result["documents"]
        ]

        # Generate answer
        answer = self.generate_answer(question, context_docs, model=model)

        return {
            "question": question,
            "answer": answer,
            "sources": retrieval_result["documents"],
            "num_sources": len(context_docs)
        }

    def load_existing(self) -> bool:
        """
        Load existing vectorstore

        Returns:
            True if loaded successfully
        """
        try:
            self.vectorstore.load()
            self.is_initialized = True
            logger.info("Loaded existing vectorstore")
            return True
        except Exception as e:
            logger.warning(f"Could not load existing vectorstore: {str(e)}")
            return False

    def reset(self):
        """Delete vectorstore and reset pipeline"""
        self.vectorstore.delete()
        self.is_initialized = False
        logger.info("Pipeline reset")


# Example usage
if __name__ == "__main__":
    # Initialize pipeline
    pipeline = RAGPipeline(
        embedding_provider="huggingface",  # Use "openai" for production
        chunk_size=1000,
        chunk_overlap=200
    )

    # Try to load existing vectorstore
    if not pipeline.load_existing():
        # Ingest documents
        stats = pipeline.ingest_documents("data/documents")
        print(f"Ingestion stats: {stats}")

    # Query
    result = pipeline.chat("What is ROS 2?", k=3)
    print(f"\nQuestion: {result['question']}")
    print(f"Answer: {result['answer']}")
    print(f"Sources: {result['num_sources']}")
