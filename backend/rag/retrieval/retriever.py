"""
Document Retrieval and Reranking Module
Handles semantic search and result reranking
"""
from typing import List, Tuple, Optional
from langchain.schema import Document
from rank_bm25 import BM25Okapi
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HybridRetriever:
    """
    Combines vector similarity search with BM25 keyword search
    and reranks results for optimal relevance
    """

    def __init__(self, vectorstore, bm25_weight: float = 0.3):
        """
        Initialize hybrid retriever

        Args:
            vectorstore: FAISS or other vector store instance
            bm25_weight: Weight for BM25 scores (0-1), remaining weight for vector similarity
        """
        self.vectorstore = vectorstore
        self.bm25_weight = bm25_weight
        self.vector_weight = 1.0 - bm25_weight

        self.bm25: Optional[BM25Okapi] = None
        self.documents: List[Document] = []

        logger.info(f"Hybrid retriever initialized (BM25: {bm25_weight}, Vector: {self.vector_weight})")

    def index_documents_for_bm25(self, documents: List[Document]):
        """
        Index documents for BM25 keyword search

        Args:
            documents: List of documents to index
        """
        self.documents = documents

        # Tokenize documents for BM25
        tokenized_docs = [doc.page_content.lower().split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized_docs)

        logger.info(f"Indexed {len(documents)} documents for BM25")

    def retrieve(
        self,
        query: str,
        k: int = 10,
        use_hybrid: bool = True,
        rerank: bool = True
    ) -> List[Document]:
        """
        Retrieve relevant documents using hybrid search

        Args:
            query: Search query
            k: Number of documents to retrieve
            use_hybrid: Whether to combine vector and BM25 search
            rerank: Whether to rerank results

        Returns:
            List of most relevant documents
        """
        if use_hybrid and self.bm25 is not None:
            results = self._hybrid_search(query, k)
        else:
            results = self.vectorstore.similarity_search(query, k=k)

        if rerank:
            results = self._rerank_results(query, results, k)

        logger.info(f"Retrieved {len(results)} documents for query")
        return results

    def _hybrid_search(self, query: str, k: int) -> List[Document]:
        """
        Perform hybrid vector + BM25 search

        Args:
            query: Search query
            k: Number of results

        Returns:
            Combined and scored results
        """
        # Vector search
        vector_results = self.vectorstore.similarity_search_with_score(query, k=k*2)

        # BM25 search
        query_tokens = query.lower().split()
        bm25_scores = self.bm25.get_scores(query_tokens)

        # Normalize scores
        if len(vector_results) > 0:
            max_vector_score = max([score for _, score in vector_results])
            min_vector_score = min([score for _, score in vector_results])

            # Normalize to 0-1 (invert because lower distance = higher similarity)
            normalized_vector = {
                doc.page_content: 1 - (score - min_vector_score) / (max_vector_score - min_vector_score + 1e-10)
                for doc, score in vector_results
            }
        else:
            normalized_vector = {}

        # Normalize BM25 scores
        max_bm25 = max(bm25_scores) if len(bm25_scores) > 0 else 1
        normalized_bm25 = bm25_scores / (max_bm25 + 1e-10)

        # Combine scores
        combined_scores = {}
        for i, doc in enumerate(self.documents):
            vector_score = normalized_vector.get(doc.page_content, 0)
            bm25_score = normalized_bm25[i]

            combined_score = (
                self.vector_weight * vector_score +
                self.bm25_weight * bm25_score
            )

            combined_scores[i] = combined_score

        # Get top-k by combined score
        top_indices = sorted(
            combined_scores.keys(),
            key=lambda x: combined_scores[x],
            reverse=True
        )[:k]

        results = [self.documents[i] for i in top_indices]
        return results

    def _rerank_results(
        self,
        query: str,
        results: List[Document],
        k: int
    ) -> List[Document]:
        """
        Rerank results using cross-encoder or other advanced methods

        Args:
            query: Original query
            results: Initial retrieval results
            k: Final number of results to return

        Returns:
            Reranked documents
        """
        # Simple reranking based on query term frequency
        # In production, use cross-encoder models like ms-marco-MiniLM

        query_terms = set(query.lower().split())

        def score_document(doc: Document) -> float:
            content_lower = doc.page_content.lower()

            # Count query term occurrences
            term_freq = sum(content_lower.count(term) for term in query_terms)

            # Boost score if query terms appear in metadata (e.g., title)
            metadata_boost = 0
            if 'title' in doc.metadata:
                title_lower = str(doc.metadata['title']).lower()
                metadata_boost = sum(2 for term in query_terms if term in title_lower)

            return term_freq + metadata_boost

        # Score and sort
        scored_docs = [(doc, score_document(doc)) for doc in results]
        scored_docs.sort(key=lambda x: x[1], reverse=True)

        reranked = [doc for doc, score in scored_docs[:k]]
        return reranked

    def retrieve_with_scores(
        self,
        query: str,
        k: int = 10
    ) -> List[Tuple[Document, float]]:
        """
        Retrieve documents with relevance scores

        Args:
            query: Search query
            k: Number of results

        Returns:
            List of (Document, score) tuples
        """
        results = self.vectorstore.similarity_search_with_score(query, k=k)
        logger.info(f"Retrieved {len(results)} documents with scores")
        return results


class ContextualCompressor:
    """Compresses retrieved documents to only relevant parts"""

    def __init__(self, max_tokens: int = 500):
        """
        Initialize compressor

        Args:
            max_tokens: Maximum tokens per compressed document
        """
        self.max_tokens = max_tokens

    def compress(self, query: str, documents: List[Document]) -> List[Document]:
        """
        Extract only relevant portions of documents

        Args:
            query: Search query
            documents: Documents to compress

        Returns:
            Compressed documents
        """
        compressed = []

        for doc in documents:
            # Simple compression: extract sentences containing query terms
            query_terms = query.lower().split()
            sentences = doc.page_content.split('. ')

            relevant_sentences = [
                sent for sent in sentences
                if any(term in sent.lower() for term in query_terms)
            ]

            if relevant_sentences:
                compressed_content = '. '.join(relevant_sentences[:3])
                compressed_doc = Document(
                    page_content=compressed_content,
                    metadata={**doc.metadata, 'compressed': True}
                )
                compressed.append(compressed_doc)

        logger.info(f"Compressed {len(documents)} documents to {len(compressed)}")
        return compressed


# Example usage
if __name__ == "__main__":
    from langchain.schema import Document

    # Sample documents
    docs = [
        Document(page_content="Python is a high-level programming language", metadata={"id": 1}),
        Document(page_content="Machine learning uses Python extensively", metadata={"id": 2}),
        Document(page_content="Java is also a programming language", metadata={"id": 3}),
    ]

    # Mock vectorstore for testing
    class MockVectorstore:
        def similarity_search(self, query, k):
            return docs[:k]

        def similarity_search_with_score(self, query, k):
            return [(doc, 0.5) for doc in docs[:k]]

    # Test retriever
    retriever = HybridRetriever(MockVectorstore())
    retriever.index_documents_for_bm25(docs)

    results = retriever.retrieve("Python programming", k=2)
    print(f"Found {len(results)} results")
