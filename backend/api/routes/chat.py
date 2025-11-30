"""
RAG Chatbot API Routes (+50 points)
OpenAI GPT-4 + Qdrant Vector Search
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import time
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from app.config import settings

router = APIRouter()

# Initialize clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

COLLECTION_NAME = settings.qdrant_collection_name
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536


class ChatQuery(BaseModel):
    query: str
    user_id: Optional[int] = None
    selected_text: Optional[str] = None
    module_filter: Optional[str] = None


class Source(BaseModel):
    module: str
    chapter: str
    section: Optional[str] = None
    url: str
    relevance_score: float


class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]
    conversation_id: str
    processing_time: int
    timestamp: str


@router.post("/query", response_model=ChatResponse)
async def chat_query(query: ChatQuery):
    """
    RAG Chatbot Endpoint
    - Embeds user query with OpenAI
    - Searches Qdrant for relevant chunks
    - Generates answer with GPT-4 + context
    """
    start_time = time.time()

    try:
        # Step 1: Generate embedding for the query
        query_text = query.selected_text or query.query

        embedding_response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=query_text
        )
        query_embedding = embedding_response.data[0].embedding

        # Step 2: Search Qdrant for relevant chunks
        search_filter = None
        if query.module_filter:
            search_filter = Filter(
                must=[
                    FieldCondition(
                        key="module",
                        match=MatchValue(value=query.module_filter)
                    )
                ]
            )

        search_results = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_embedding,
            query_filter=search_filter,
            limit=5  # Top 5 most relevant chunks
        )

        # Step 3: Build context from retrieved chunks
        context_parts = []
        sources = []

        for idx, result in enumerate(search_results):
            payload = result.payload
            context_parts.append(
                f"[Source {idx + 1}] ({payload.get('file', 'unknown')})\n{payload.get('content', '')}\n"
            )

            sources.append(Source(
                module=payload.get('module', 'Unknown'),
                chapter=payload.get('chapter', 'Unknown'),
                section=payload.get('section'),
                url=payload.get('url', '/'),
                relevance_score=round(result.score, 3)
            ))

        context = "\n".join(context_parts)

        # Step 4: Generate answer with GPT-4
        system_prompt = """You are an expert AI assistant for the Physical AI & Humanoid Robotics textbook.

Your role:
- Answer questions accurately using ONLY the provided context
- Cite sources using [Source N] notation
- If the context doesn't contain the answer, say so clearly
- Be concise but comprehensive
- Use technical terminology appropriately

Format your responses with:
- Clear explanations
- Code examples when relevant
- References to specific modules/chapters"""

        user_prompt = f"""Context from the textbook:
{context}

User Question: {query.query}

Please provide a detailed answer based ONLY on the context above. Include source citations."""

        completion = openai_client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,  # Lower temperature for more accurate responses
            max_tokens=800
        )

        answer = completion.choices[0].message.content

        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)  # milliseconds

        return ChatResponse(
            answer=answer,
            sources=sources,
            conversation_id=f"conv_{int(time.time())}",
            processing_time=processing_time,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        )

    except Exception as e:
        # Log error
        print(f"RAG Error: {str(e)}")

        # Return fallback response
        raise HTTPException(
            status_code=500,
            detail=f"RAG processing error: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Check if RAG system is operational
    """
    try:
        # Check OpenAI API
        openai_status = "connected" if os.getenv("OPENAI_API_KEY") else "missing_api_key"

        # Check Qdrant
        try:
            collections = qdrant_client.get_collections()
            qdrant_status = "connected"
            collection_exists = any(c.name == COLLECTION_NAME for c in collections.collections)
        except:
            qdrant_status = "disconnected"
            collection_exists = False

        return {
            "status": "healthy" if (openai_status == "connected" and collection_exists) else "degraded",
            "services": {
                "openai": openai_status,
                "qdrant": qdrant_status,
                "collection_exists": collection_exists,
                "collection_name": COLLECTION_NAME
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@router.get("/history/{user_id}")
async def get_chat_history(user_id: int, limit: int = 10):
    """Get chat history for a user (Future: implement with database)"""
    # TODO: Implement database query for chat history
    return {
        "user_id": user_id,
        "messages": [],
        "note": "Chat history feature will be implemented in Phase 2"
    }
