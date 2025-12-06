"""
Configuration module for loading environment variables.

This module provides centralized configuration management using Pydantic Settings
to ensure type safety and validation of environment variables.
"""

import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Uses pydantic-settings for automatic validation and type conversion.
    All sensitive values (API keys, database URLs) must be set via environment.
    """

    # OpenAI Configuration
    openai_api_key: str
    openai_chat_model: str = "gpt-4"
    openai_embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536

    # Qdrant Configuration
    qdrant_url: str
    qdrant_api_key: str
    qdrant_collection_name: str = "content_embeddings"
    qdrant_top_k: int = 5  # Number of results to retrieve
    qdrant_timeout: float = 0.2  # 200ms timeout for vector search

    # Neon Postgres Configuration
    database_url: str

    # FastAPI Configuration
    cors_origins: str = "http://localhost:3000"  # Comma-separated list
    environment: str = "development"

    # Performance settings
    max_requests_per_minute: int = 100
    response_timeout: float = 3.0  # End-to-end response time target (seconds)

    # Chunking configuration for embeddings
    chunk_size: int = 512  # Max tokens per chunk
    chunk_overlap: int = 50  # Token overlap between chunks

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignore extra environment variables
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Singleton instance of settings
settings = Settings()
