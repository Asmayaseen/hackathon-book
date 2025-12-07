"""
Embedding Generation Module
Creates vector embeddings for documents using OpenAI or HuggingFace models
"""
from typing import List, Optional
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
from langchain.schema import Document
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Handles creation of document embeddings"""

    def __init__(
        self,
        provider: str = "openai",
        model_name: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize embedding generator

        Args:
            provider: "openai" or "huggingface"
            model_name: Specific model to use
            api_key: API key for OpenAI (if applicable)
        """
        self.provider = provider

        if provider == "openai":
            self.model_name = model_name or "text-embedding-3-small"
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")

            self.embeddings = OpenAIEmbeddings(
                model=self.model_name,
                openai_api_key=self.api_key
            )

            logger.info(f"Initialized OpenAI embeddings: {self.model_name}")

        elif provider == "huggingface":
            self.model_name = model_name or "sentence-transformers/all-MiniLM-L6-v2"

            self.embeddings = HuggingFaceEmbeddings(
                model_name=self.model_name,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )

            logger.info(f"Initialized HuggingFace embeddings: {self.model_name}")

        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple documents

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        try:
            embeddings = self.embeddings.embed_documents(texts)
            logger.info(f"Generated embeddings for {len(texts)} documents")
            return embeddings

        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise

    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a single query

        Args:
            text: Query text to embed

        Returns:
            Embedding vector
        """
        try:
            embedding = self.embeddings.embed_query(text)
            logger.info("Generated query embedding")
            return embedding

        except Exception as e:
            logger.error(f"Error generating query embedding: {str(e)}")
            raise

    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by this model

        Returns:
            Embedding dimension
        """
        test_embedding = self.embed_query("test")
        return len(test_embedding)

    async def embed_documents_async(self, texts: List[str]) -> List[List[float]]:
        """
        Async version of embed_documents for better performance

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        try:
            if hasattr(self.embeddings, 'aembed_documents'):
                embeddings = await self.embeddings.aembed_documents(texts)
            else:
                # Fallback to sync version
                embeddings = self.embed_documents(texts)

            logger.info(f"Generated embeddings (async) for {len(texts)} documents")
            return embeddings

        except Exception as e:
            logger.error(f"Error generating embeddings (async): {str(e)}")
            raise


class EmbeddingCache:
    """Simple in-memory cache for embeddings"""

    def __init__(self):
        self.cache = {}
        logger.info("Embedding cache initialized")

    def get(self, text: str) -> Optional[List[float]]:
        """Get cached embedding for text"""
        return self.cache.get(text)

    def set(self, text: str, embedding: List[float]):
        """Cache embedding for text"""
        self.cache[text] = embedding

    def clear(self):
        """Clear all cached embeddings"""
        self.cache.clear()
        logger.info("Embedding cache cleared")

    def size(self) -> int:
        """Get number of cached embeddings"""
        return len(self.cache)


# Example usage
if __name__ == "__main__":
    # Test OpenAI embeddings
    try:
        openai_gen = EmbeddingGenerator(provider="openai")
        test_texts = ["Hello world", "This is a test"]
        embeddings = openai_gen.embed_documents(test_texts)
        print(f"OpenAI: Generated {len(embeddings)} embeddings")
        print(f"Dimension: {openai_gen.get_embedding_dimension()}")
    except Exception as e:
        print(f"OpenAI error: {e}")

    # Test HuggingFace embeddings (always works, doesn't need API key)
    hf_gen = EmbeddingGenerator(provider="huggingface")
    test_texts = ["Hello world", "This is a test"]
    embeddings = hf_gen.embed_documents(test_texts)
    print(f"HuggingFace: Generated {len(embeddings)} embeddings")
    print(f"Dimension: {hf_gen.get_embedding_dimension()}")
