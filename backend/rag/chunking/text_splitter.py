"""
Text Chunking Module
Splits documents into optimal chunks for embedding and retrieval
"""
from typing import List
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    TokenTextSplitter,
    MarkdownTextSplitter
)
from langchain.schema import Document
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentChunker:
    """Handles splitting documents into chunks for embedding"""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: List[str] = None
    ):
        """
        Initialize chunker with configurable parameters

        Args:
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Overlap between consecutive chunks
            separators: Custom separators for splitting
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Default separators optimized for technical content
        if separators is None:
            separators = [
                "\n\n\n",  # Multiple newlines (sections)
                "\n\n",    # Paragraphs
                "\n",      # Lines
                ". ",      # Sentences
                ", ",      # Clauses
                " ",       # Words
                ""         # Characters
            ]

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            length_function=len
        )

        logger.info(f"Chunker initialized: size={chunk_size}, overlap={chunk_overlap}")

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks

        Args:
            documents: List of Document objects to chunk

        Returns:
            List of chunked Document objects with preserved metadata
        """
        try:
            chunked_docs = self.text_splitter.split_documents(documents)

            # Add chunk index to metadata
            for idx, doc in enumerate(chunked_docs):
                doc.metadata["chunk_id"] = idx
                doc.metadata["chunk_size"] = len(doc.page_content)

            logger.info(
                f"Split {len(documents)} documents into {len(chunked_docs)} chunks"
            )

            return chunked_docs

        except Exception as e:
            logger.error(f"Error chunking documents: {str(e)}")
            raise

    def chunk_markdown(self, documents: List[Document]) -> List[Document]:
        """
        Split markdown documents preserving structure

        Args:
            documents: List of markdown Document objects

        Returns:
            List of chunked Documents
        """
        md_splitter = MarkdownTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )

        try:
            chunked_docs = md_splitter.split_documents(documents)

            for idx, doc in enumerate(chunked_docs):
                doc.metadata["chunk_id"] = idx
                doc.metadata["chunk_size"] = len(doc.page_content)

            logger.info(
                f"Split {len(documents)} markdown documents into {len(chunked_docs)} chunks"
            )

            return chunked_docs

        except Exception as e:
            logger.error(f"Error chunking markdown: {str(e)}")
            raise

    def chunk_by_tokens(
        self,
        documents: List[Document],
        model_name: str = "gpt-3.5-turbo"
    ) -> List[Document]:
        """
        Split documents by token count (useful for LLM context limits)

        Args:
            documents: List of Document objects
            model_name: Model name for tokenization

        Returns:
            List of chunked Documents
        """
        token_splitter = TokenTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            model_name=model_name
        )

        try:
            chunked_docs = token_splitter.split_documents(documents)

            for idx, doc in enumerate(chunked_docs):
                doc.metadata["chunk_id"] = idx

            logger.info(
                f"Split {len(documents)} documents into {len(chunked_docs)} token-based chunks"
            )

            return chunked_docs

        except Exception as e:
            logger.error(f"Error chunking by tokens: {str(e)}")
            raise

    def get_chunk_stats(self, chunks: List[Document]) -> dict:
        """
        Get statistics about chunks

        Args:
            chunks: List of chunked documents

        Returns:
            Dictionary with chunk statistics
        """
        if not chunks:
            return {"total_chunks": 0}

        chunk_sizes = [len(doc.page_content) for doc in chunks]

        stats = {
            "total_chunks": len(chunks),
            "avg_chunk_size": sum(chunk_sizes) / len(chunk_sizes),
            "min_chunk_size": min(chunk_sizes),
            "max_chunk_size": max(chunk_sizes),
            "total_characters": sum(chunk_sizes)
        }

        logger.info(f"Chunk statistics: {stats}")
        return stats


# Example usage
if __name__ == "__main__":
    from langchain.schema import Document

    # Example document
    sample_doc = Document(
        page_content="This is a long document. " * 100,
        metadata={"source": "example.txt"}
    )

    chunker = DocumentChunker(chunk_size=500, chunk_overlap=50)
    chunks = chunker.chunk_documents([sample_doc])

    print(f"Created {len(chunks)} chunks")
    print(chunker.get_chunk_stats(chunks))
