"""
RAG (Retrieval-Augmented Generation) service for vector search.

Handles communication with Qdrant vector database to retrieve
relevant textbook passages based on semantic similarity.
"""

import logging
from typing import List, Dict, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

from app.config import settings
from app.services.embedding_service import embedding_service

logger = logging.getLogger(__name__)


class RAGService:
    """
    Service for retrieving relevant passages from vector database.

    Uses Qdrant Cloud for fast similarity search (<200ms) to find
    the top K most relevant textbook sections for a given query.
    """

    def __init__(self):
        """Initialize Qdrant client and ensure collection exists."""
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            timeout=settings.qdrant_timeout
        )
        self.collection_name = settings.qdrant_collection_name
        self.top_k = settings.qdrant_top_k

        logger.info(f"Initialized RAGService with collection: {self.collection_name}")

        # Ensure collection exists (for development - seed script creates it)
        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        """
        Create collection if it doesn't exist.

        Uses HNSW index for fast approximate nearest neighbor search
        with cosine similarity metric.
        """
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]

            if self.collection_name not in collection_names:
                logger.warning(f"Collection '{self.collection_name}' not found. Creating...")

                # Create collection with HNSW index
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=settings.embedding_dimensions,
                        distance=Distance.COSINE  # Cosine similarity for semantic search
                    ),
                    # HNSW parameters for performance
                    hnsw_config={
                        "m": 16,  # Number of edges per node
                        "ef_construct": 100  # Size of dynamic candidate list
                    }
                )
                logger.info(f"Created collection '{self.collection_name}'")
            else:
                logger.info(f"Collection '{self.collection_name}' already exists")

        except Exception as e:
            logger.error(f"Error ensuring collection exists: {e}")
            # Don't raise - allow app to start even if Qdrant is unavailable

    def retrieve_relevant_passages(
        self,
        query: str,
        module_filter: Optional[str] = None,
        top_k: Optional[int] = None
    ) -> List[Dict]:
        """
        Retrieve top K most relevant passages for a query.

        Process:
        1. Generate embedding for query text
        2. Search Qdrant for similar vectors
        3. Return passages with metadata (module, chapter, URL)

        Args:
            query: User's question or search query
            module_filter: Optional module name to filter results (e.g., "module-01-ros2")
            top_k: Number of results to return (defaults to settings.qdrant_top_k)

        Returns:
            List of dicts with keys: text, module, chapter, section, url, score

        Raises:
            Exception if embedding generation or vector search fails
        """
        try:
            # Generate query embedding
            query_embedding = embedding_service.generate_embedding(query)

            # Prepare search filter if module specified
            search_filter = None
            if module_filter:
                search_filter = Filter(
                    must=[
                        FieldCondition(
                            key="module",
                            match=MatchValue(value=module_filter)
                        )
                    ]
                )

            # Search Qdrant for similar vectors
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=search_filter,
                limit=top_k or self.top_k,
                with_payload=True  # Include metadata
            )

            # Extract passages with metadata
            passages = []
            for result in search_results:
                passage = {
                    "text": result.payload.get("text", ""),
                    "module": result.payload.get("module", "Unknown Module"),
                    "chapter": result.payload.get("chapter", "Unknown Chapter"),
                    "section": result.payload.get("section", None),
                    "url": result.payload.get("url", ""),
                    "score": result.score  # Similarity score (0-1 for cosine)
                }
                passages.append(passage)

            logger.info(f"Retrieved {len(passages)} relevant passages for query: {query[:50]}...")

            return passages

        except Exception as e:
            logger.error(f"Error retrieving passages: {e}")
            raise


# Singleton instance for dependency injection
rag_service = RAGService()
