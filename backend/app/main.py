"""
Main FastAPI application entry point.

This module initializes the FastAPI app with CORS middleware, routes,
and error handling for the RAG chatbot API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.api import chat

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events.

    Handles initialization and cleanup of database connections,
    vector store clients, and other resources.
    """
    logger.info("Starting up RAG chatbot API...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"CORS Origins: {settings.cors_origins_list}")

    # Startup logic would go here (e.g., initialize DB pool, Qdrant client)
    # For now, connections are initialized on-demand in services

    yield

    # Shutdown logic
    logger.info("Shutting down RAG chatbot API...")


# Initialize FastAPI application
app = FastAPI(
    title="Physical AI RAG Chatbot API",
    description="Retrieval-Augmented Generation chatbot for Physical AI & Humanoid Robotics textbook",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,  # Frontend URLs (localhost + GitHub Pages)
    allow_credentials=True,  # Allow cookies for session management
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Allowed HTTP methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],  # Expose all response headers
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Include API routers
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "Physical AI RAG Chatbot API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """
    Detailed health check endpoint.

    Returns API status and configuration (without exposing secrets).
    """
    return {
        "status": "healthy",
        "environment": settings.environment,
        "openai_model": settings.openai_chat_model,
        "embedding_model": settings.openai_embedding_model,
        "qdrant_collection": settings.qdrant_collection_name,
        "max_response_time": f"{settings.response_timeout}s"
    }


if __name__ == "__main__":
    import uvicorn

    # Run with: python -m app.main
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "development"
    )
