"""
FAISS Vector Database Module
Handles storage and retrieval of document embeddings using FAISS
"""
from typing import List, Optional, Tuple
from pathlib import Path
import pickle
import logging

from langchain.vectorstores import FAISS
from langchain.schema import Document
from langchain.embeddings.base import Embeddings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FAISSVectorStore:
    """Manages FAISS vector database for document retrieval"""

    def __init__(
        self,
        embeddings: Embeddings,
        persist_directory: str = "data/vectorstore"
    ):
        """
        Initialize FAISS vector store

        Args:
            embeddings: Embedding generator instance
            persist_directory: Directory to save/load vector store
        """
        self.embeddings = embeddings
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        self.vectorstore: Optional[FAISS] = None
        self.index_path = self.persist_directory / "faiss_index"
        self.docs_path = self.persist_directory / "documents.pkl"

        logger.info(f"FAISS store initialized at {persist_directory}")

    def create_from_documents(self, documents: List[Document]) -> FAISS:
        """
        Create new FAISS index from documents

        Args:
            documents: List of Document objects with text and metadata

        Returns:
            FAISS vectorstore
        """
        try:
            logger.info(f"Creating FAISS index from {len(documents)} documents...")

            self.vectorstore = FAISS.from_documents(
                documents=documents,
                embedding=self.embeddings
            )

            logger.info("FAISS index created successfully")
            return self.vectorstore

        except Exception as e:
            logger.error(f"Error creating FAISS index: {str(e)}")
            raise

    def add_documents(self, documents: List[Document]):
        """
        Add new documents to existing vectorstore

        Args:
            documents: List of Document objects to add
        """
        if self.vectorstore is None:
            raise ValueError("Vectorstore not initialized. Create or load first.")

        try:
            self.vectorstore.add_documents(documents)
            logger.info(f"Added {len(documents)} documents to vectorstore")

        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise

    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[dict] = None
    ) -> List[Document]:
        """
        Search for similar documents

        Args:
            query: Search query
            k: Number of results to return
            filter: Optional metadata filter

        Returns:
            List of most similar documents
        """
        if self.vectorstore is None:
            raise ValueError("Vectorstore not initialized. Create or load first.")

        try:
            results = self.vectorstore.similarity_search(
                query=query,
                k=k,
                filter=filter
            )

            logger.info(f"Found {len(results)} similar documents for query")
            return results

        except Exception as e:
            logger.error(f"Error in similarity search: {str(e)}")
            raise

    def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        filter: Optional[dict] = None
    ) -> List[Tuple[Document, float]]:
        """
        Search with similarity scores

        Args:
            query: Search query
            k: Number of results to return
            filter: Optional metadata filter

        Returns:
            List of tuples (Document, score)
        """
        if self.vectorstore is None:
            raise ValueError("Vectorstore not initialized. Create or load first.")

        try:
            results = self.vectorstore.similarity_search_with_score(
                query=query,
                k=k,
                filter=filter
            )

            logger.info(f"Found {len(results)} documents with scores")
            return results

        except Exception as e:
            logger.error(f"Error in similarity search with score: {str(e)}")
            raise

    def max_marginal_relevance_search(
        self,
        query: str,
        k: int = 4,
        fetch_k: int = 20,
        lambda_mult: float = 0.5
    ) -> List[Document]:
        """
        MMR search for diverse results

        Args:
            query: Search query
            k: Number of results to return
            fetch_k: Number of documents to fetch for MMR
            lambda_mult: Diversity parameter (0=max diversity, 1=max relevance)

        Returns:
            List of diverse relevant documents
        """
        if self.vectorstore is None:
            raise ValueError("Vectorstore not initialized. Create or load first.")

        try:
            results = self.vectorstore.max_marginal_relevance_search(
                query=query,
                k=k,
                fetch_k=fetch_k,
                lambda_mult=lambda_mult
            )

            logger.info(f"MMR search returned {len(results)} diverse documents")
            return results

        except Exception as e:
            logger.error(f"Error in MMR search: {str(e)}")
            raise

    def save(self):
        """Save vector store to disk"""
        if self.vectorstore is None:
            raise ValueError("No vectorstore to save")

        try:
            # Save FAISS index
            self.vectorstore.save_local(str(self.index_path))
            logger.info(f"Vectorstore saved to {self.index_path}")

        except Exception as e:
            logger.error(f"Error saving vectorstore: {str(e)}")
            raise

    def load(self) -> FAISS:
        """
        Load vector store from disk

        Returns:
            Loaded FAISS vectorstore
        """
        try:
            if not self.index_path.exists():
                raise FileNotFoundError(f"No vectorstore found at {self.index_path}")

            self.vectorstore = FAISS.load_local(
                str(self.index_path),
                self.embeddings,
                allow_dangerous_deserialization=True  # Required for FAISS
            )

            logger.info(f"Vectorstore loaded from {self.index_path}")
            return self.vectorstore

        except Exception as e:
            logger.error(f"Error loading vectorstore: {str(e)}")
            raise

    def delete(self):
        """Delete saved vectorstore files"""
        try:
            import shutil

            if self.index_path.exists():
                shutil.rmtree(self.index_path)
                logger.info("Vectorstore files deleted")
            else:
                logger.warning("No vectorstore files to delete")

        except Exception as e:
            logger.error(f"Error deleting vectorstore: {str(e)}")
            raise

    def get_stats(self) -> dict:
        """
        Get statistics about the vectorstore

        Returns:
            Dictionary with vectorstore stats
        """
        if self.vectorstore is None:
            return {"status": "not_initialized"}

        try:
            index = self.vectorstore.index
            stats = {
                "status": "initialized",
                "total_vectors": index.ntotal,
                "dimension": index.d,
                "is_trained": index.is_trained
            }

            logger.info(f"Vectorstore stats: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            return {"status": "error", "error": str(e)}


# Example usage
if __name__ == "__main__":
    from langchain.embeddings import OpenAIEmbeddings
    from langchain.schema import Document

    # Initialize embeddings
    embeddings = OpenAIEmbeddings()

    # Create sample documents
    docs = [
        Document(page_content="Python is a programming language", metadata={"source": "doc1"}),
        Document(page_content="Machine learning uses neural networks", metadata={"source": "doc2"}),
    ]

    # Create vector store
    store = FAISSVectorStore(embeddings)
    store.create_from_documents(docs)

    # Search
    results = store.similarity_search("What is Python?", k=1)
    print(f"Found: {results[0].page_content}")

    # Save and load
    store.save()
    store.load()

    print(store.get_stats())
