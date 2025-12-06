"""
Chat API endpoints for RAG chatbot.

Provides POST /query endpoint for submitting questions and
receiving AI-generated responses with source citations.
"""

import logging
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from app.models.chat import ChatRequest, ChatResponse
from app.services.chatbot_service import chatbot_service
from app.config import settings

logger = logging.getLogger(__name__)

# Create router for chat endpoints
router = APIRouter()


@router.post("/query", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def query_chatbot(request: ChatRequest) -> ChatResponse:
    """
    Process user query and return AI-generated response.

    This endpoint orchestrates the full RAG pipeline:
    1. Receives user query (with optional context)
    2. Retrieves relevant textbook passages via vector search
    3. Generates response using GPT-4 with citations
    4. Returns answer with source references

    Performance requirements:
    - Vector search: <200ms (FR-007)
    - End-to-end response: <3 seconds (FR-008)
    - Accuracy: >85% on validation set (FR-010)

    Args:
        request: ChatRequest with query, optional conversation_id, selected_text, module_filter

    Returns:
        ChatResponse with answer, sources, conversation_id, timing

    Raises:
        HTTPException 400: Invalid request (empty query, etc.)
        HTTPException 500: Server error during processing
        HTTPException 503: External service unavailable (OpenAI, Qdrant)
    """
    try:
        # Validate query
        if not request.query or not request.query.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query cannot be empty"
            )

        logger.info(f"Received chat query: {request.query[:100]}...")

        # Generate response using chatbot service
        response = chatbot_service.generate_response(
            query=request.query,
            conversation_id=request.conversation_id,
            selected_text=request.selected_text,
            module_filter=request.module_filter
        )

        # Check response time against SLA
        if response.processing_time > settings.response_timeout:
            logger.warning(
                f"Response time {response.processing_time:.2f}s exceeds target {settings.response_timeout}s"
            )

        logger.info(f"Returned response with {len(response.sources)} sources in {response.processing_time:.2f}s")

        return response

    except HTTPException:
        # Re-raise HTTP exceptions (already have proper status codes)
        raise

    except Exception as e:
        # Log unexpected errors and return 500
        logger.error(f"Error processing chat query: {e}", exc_info=True)

        # Check if it's an OpenAI API error
        if "openai" in str(type(e)).lower():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="OpenAI API is currently unavailable. Please try again later."
            )

        # Check if it's a Qdrant error
        if "qdrant" in str(type(e)).lower():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Vector database is currently unavailable. Please try again later."
            )

        # Generic server error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your query. Please try again."
        )


@router.get("/health", status_code=status.HTTP_200_OK)
async def chat_health_check():
    """
    Health check endpoint for chat service.

    Returns status of chatbot dependencies.
    """
    return {
        "status": "healthy",
        "service": "chat",
        "model": settings.openai_chat_model,
        "embedding_model": settings.openai_embedding_model,
        "max_response_time": f"{settings.response_timeout}s"
    }
