"""
Document Ingestion Module
Handles loading of PDF and text files for RAG system
"""
import os
from typing import List, Dict, Optional
from pathlib import Path
import pdfplumber
from langchain.schema import Document
from langchain.document_loaders import TextLoader, DirectoryLoader
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentLoader:
    """Handles loading documents from various sources"""

    def __init__(self, data_dir: str = "data/documents"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def load_pdf(self, pdf_path: str) -> List[Document]:
        """
        Load and extract text from PDF file

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of Document objects with extracted text
        """
        documents = []

        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()

                    if text and text.strip():
                        doc = Document(
                            page_content=text,
                            metadata={
                                "source": pdf_path,
                                "page": page_num + 1,
                                "type": "pdf"
                            }
                        )
                        documents.append(doc)

            logger.info(f"Loaded {len(documents)} pages from {pdf_path}")
            return documents

        except Exception as e:
            logger.error(f"Error loading PDF {pdf_path}: {str(e)}")
            raise

    def load_text(self, text_path: str) -> List[Document]:
        """
        Load text from .txt or .md file

        Args:
            text_path: Path to text file

        Returns:
            List containing single Document object
        """
        try:
            with open(text_path, 'r', encoding='utf-8') as f:
                text = f.read()

            doc = Document(
                page_content=text,
                metadata={
                    "source": text_path,
                    "type": "text"
                }
            )

            logger.info(f"Loaded text file: {text_path}")
            return [doc]

        except Exception as e:
            logger.error(f"Error loading text file {text_path}: {str(e)}")
            raise

    def load_directory(self, directory_path: str, file_types: Optional[List[str]] = None) -> List[Document]:
        """
        Load all documents from a directory

        Args:
            directory_path: Path to directory
            file_types: List of file extensions to load (e.g., ['.pdf', '.txt'])

        Returns:
            List of all loaded documents
        """
        if file_types is None:
            file_types = ['.pdf', '.txt', '.md']

        all_documents = []
        directory = Path(directory_path)

        for file_type in file_types:
            files = list(directory.rglob(f"*{file_type}"))

            for file_path in files:
                try:
                    if file_type == '.pdf':
                        docs = self.load_pdf(str(file_path))
                    else:
                        docs = self.load_text(str(file_path))

                    all_documents.extend(docs)

                except Exception as e:
                    logger.warning(f"Skipping {file_path}: {str(e)}")
                    continue

        logger.info(f"Loaded total {len(all_documents)} documents from {directory_path}")
        return all_documents

    def load_from_url(self, url: str) -> List[Document]:
        """
        Load document from URL (for future implementation)

        Args:
            url: URL to document

        Returns:
            List of Document objects
        """
        # TODO: Implement web scraping functionality
        raise NotImplementedError("URL loading not yet implemented")


# Example usage
if __name__ == "__main__":
    loader = DocumentLoader()

    # Load single PDF
    # docs = loader.load_pdf("path/to/document.pdf")

    # Load entire directory
    # docs = loader.load_directory("data/documents")

    print("Document loader initialized successfully")
