"""
Embedding service for generating text embeddings using OpenAI.

Provides wrapper around OpenAI's text-embedding-3-small model
with retry logic and error handling.
"""

import logging
from typing import List
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service for generating text embeddings.

    Uses OpenAI's text-embedding-3-small model (1536 dimensions)
    for converting text into vector representations.
    """

    def __init__(self):
        """Initialize OpenAI client with API key from settings."""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_embedding_model
        self.dimensions = settings.embedding_dimensions
        logger.info(f"Initialized EmbeddingService with model: {self.model}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True
    )
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for a single text string.

        Uses retry logic to handle transient API failures.

        Args:
            text: Input text to embed (will be truncated if too long)

        Returns:
            List of floats representing the embedding vector (1536 dimensions)

        Raises:
            OpenAI API errors after 3 retry attempts
        """
        try:
            # Call OpenAI embeddings API
            response = self.client.embeddings.create(
                model=self.model,
                input=text,
                encoding_format="float"  # Return as list of floats
            )

            embedding = response.data[0].embedding
            logger.debug(f"Generated embedding for text of length {len(text)} chars")

            return embedding

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True
    )
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in a single API call.

        More efficient than calling generate_embedding repeatedly.
        Useful for batch processing during seed script.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors, one per input text

        Raises:
            OpenAI API errors after 3 retry attempts
        """
        try:
            # Batch API call (max 2048 texts per request)
            response = self.client.embeddings.create(
                model=self.model,
                input=texts,
                encoding_format="float"
            )

            embeddings = [item.embedding for item in response.data]
            logger.info(f"Generated {len(embeddings)} embeddings in batch")

            return embeddings

        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise


# Singleton instance for dependency injection
embedding_service = EmbeddingService()
