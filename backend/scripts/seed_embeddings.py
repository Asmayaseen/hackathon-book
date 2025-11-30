"""
Seed embeddings script for populating Qdrant vector database.

Reads all markdown files from frontend/docs/, chunks them into
512-token segments (sentence-grouped), generates embeddings,
and uploads to Qdrant with metadata (module, chapter, url).

Usage:
    python backend/scripts/seed_embeddings.py
"""

import os
import sys
import re
import logging
from pathlib import Path
from typing import List, Dict
import tiktoken
from tqdm import tqdm

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.services.embedding_service import embedding_service
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MarkdownChunker:
    """
    Chunks markdown content into semantically meaningful segments.

    Uses sentence boundaries to preserve context and limits chunks
    to max 512 tokens (as specified in requirements).
    """

    def __init__(self, max_tokens: int = 512, overlap_tokens: int = 50):
        """
        Initialize chunker with token limits.

        Args:
            max_tokens: Maximum tokens per chunk
            overlap_tokens: Number of tokens to overlap between chunks
        """
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens
        # Use tiktoken for accurate token counting (matches OpenAI's tokenization)
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

    def chunk_text(self, text: str) -> List[str]:
        """
        Chunk text into segments at sentence boundaries.

        Process:
        1. Split text into sentences
        2. Group sentences until reaching max_tokens
        3. Add overlap between chunks for context continuity

        Args:
            text: Input markdown text

        Returns:
            List of text chunks (each <= max_tokens)
        """
        # Split into sentences (basic approach - handles most cases)
        sentences = re.split(r'(?<=[.!?])\s+', text)

        chunks = []
        current_chunk = []
        current_tokens = 0

        for sentence in sentences:
            sentence_tokens = len(self.encoding.encode(sentence))

            # If adding this sentence exceeds limit, save current chunk
            if current_tokens + sentence_tokens > self.max_tokens and current_chunk:
                chunks.append(" ".join(current_chunk))

                # Start new chunk with overlap (last few sentences)
                overlap = []
                overlap_tokens = 0
                for s in reversed(current_chunk):
                    s_tokens = len(self.encoding.encode(s))
                    if overlap_tokens + s_tokens <= self.overlap_tokens:
                        overlap.insert(0, s)
                        overlap_tokens += s_tokens
                    else:
                        break

                current_chunk = overlap
                current_tokens = overlap_tokens

            # Add sentence to current chunk
            current_chunk.append(sentence)
            current_tokens += sentence_tokens

        # Add final chunk
        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks


class MarkdownProcessor:
    """
    Processes markdown files from frontend/docs/ for embedding.

    Extracts content, metadata, and generates appropriate URLs.
    """

    def __init__(self, docs_dir: str):
        """
        Initialize processor with docs directory path.

        Args:
            docs_dir: Path to frontend/docs/ directory
        """
        self.docs_dir = Path(docs_dir)
        self.chunker = MarkdownChunker(
            max_tokens=settings.chunk_size,
            overlap_tokens=settings.chunk_overlap
        )

    def extract_metadata(self, file_path: Path) -> Dict[str, str]:
        """
        Extract module, chapter, and URL from file path.

        Args:
            file_path: Path to markdown file

        Returns:
            Dict with keys: module, chapter, section, url
        """
        # Get relative path from docs directory
        rel_path = file_path.relative_to(self.docs_dir)
        parts = rel_path.parts

        # Parse module from directory name (e.g., "module-01-ros2")
        if len(parts) > 0 and parts[0].startswith("module-"):
            module_num = parts[0].split("-")[1]  # "01"
            module_name_parts = parts[0].split("-")[2:]  # ["ros2"]
            module_name = " ".join(module_name_parts).upper()
            module = f"Module {module_num}: {module_name}"
        else:
            module = "General"

        # Parse chapter from filename (e.g., "week-3-nodes-topics.md")
        chapter = file_path.stem.replace("-", " ").title()

        # Generate URL (relative to site root)
        url_path = str(rel_path.with_suffix("")).replace("\\", "/")
        url = f"/{url_path}"

        return {
            "module": module,
            "chapter": chapter,
            "section": None,  # Could parse from headings if needed
            "url": url
        }

    def process_file(self, file_path: Path) -> List[Dict]:
        """
        Process a single markdown file into chunks with metadata.

        Args:
            file_path: Path to markdown file

        Returns:
            List of dicts with keys: text, module, chapter, section, url
        """
        try:
            # Read file content
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Remove frontmatter (YAML between --- delimiters)
            content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)

            # Remove code blocks (preserve for context but don't over-index)
            # Keep inline code, remove large code blocks
            content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)

            # Clean up markdown formatting
            content = re.sub(r'[#*_`]', '', content)  # Remove markdown symbols
            content = re.sub(r'\n\s*\n', '\n\n', content)  # Normalize whitespace

            # Skip if content too short
            if len(content.strip()) < 100:
                logger.debug(f"Skipping {file_path} (too short)")
                return []

            # Extract metadata
            metadata = self.extract_metadata(file_path)

            # Chunk content
            chunks = self.chunker.chunk_text(content)

            # Create chunk objects with metadata
            chunk_objects = []
            for i, chunk_text in enumerate(chunks):
                chunk_obj = {
                    "text": chunk_text,
                    "module": metadata["module"],
                    "chapter": metadata["chapter"],
                    "section": metadata["section"],
                    "url": metadata["url"],
                    "chunk_index": i
                }
                chunk_objects.append(chunk_obj)

            logger.debug(f"Processed {file_path}: {len(chunks)} chunks")
            return chunk_objects

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return []

    def process_all_files(self) -> List[Dict]:
        """
        Process all markdown files in docs directory.

        Returns:
            List of all chunks from all files
        """
        all_chunks = []

        # Find all .md files recursively
        md_files = list(self.docs_dir.rglob("*.md"))
        logger.info(f"Found {len(md_files)} markdown files")

        for file_path in tqdm(md_files, desc="Processing markdown files"):
            chunks = self.process_file(file_path)
            all_chunks.extend(chunks)

        logger.info(f"Generated {len(all_chunks)} total chunks")
        return all_chunks


def seed_qdrant(chunks: List[Dict]):
    """
    Upload chunks with embeddings to Qdrant.

    Args:
        chunks: List of chunk dicts with text and metadata
    """
    logger.info("Connecting to Qdrant...")
    client = QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key
    )

    collection_name = settings.qdrant_collection_name

    # Recreate collection (delete if exists)
    try:
        client.delete_collection(collection_name)
        logger.info(f"Deleted existing collection: {collection_name}")
    except Exception:
        pass  # Collection doesn't exist yet

    # Create collection
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=settings.embedding_dimensions,
            distance=Distance.COSINE  # Cosine similarity
        ),
        hnsw_config={
            "m": 16,  # Number of edges per node
            "ef_construct": 100  # Size of dynamic candidate list
        }
    )
    logger.info(f"Created collection: {collection_name}")

    # Generate embeddings and upload in batches
    batch_size = 100  # Process 100 chunks at a time
    total_batches = (len(chunks) + batch_size - 1) // batch_size

    for batch_idx in tqdm(range(0, len(chunks), batch_size), desc="Uploading to Qdrant", total=total_batches):
        batch = chunks[batch_idx:batch_idx + batch_size]

        # Generate embeddings for batch
        texts = [chunk["text"] for chunk in batch]
        embeddings = embedding_service.generate_embeddings_batch(texts)

        # Create points for Qdrant
        points = []
        for i, (chunk, embedding) in enumerate(zip(batch, embeddings)):
            point = PointStruct(
                id=batch_idx + i,  # Unique ID
                vector=embedding,
                payload={
                    "text": chunk["text"],
                    "module": chunk["module"],
                    "chapter": chunk["chapter"],
                    "section": chunk["section"],
                    "url": chunk["url"],
                    "chunk_index": chunk["chunk_index"]
                }
            )
            points.append(point)

        # Upload batch to Qdrant
        client.upsert(
            collection_name=collection_name,
            points=points
        )

    logger.info(f"Successfully uploaded {len(chunks)} chunks to Qdrant")


def main():
    """Main entry point for seeding script."""
    logger.info("=" * 60)
    logger.info("Starting embeddings seeding process")
    logger.info("=" * 60)

    # Determine docs directory path
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    docs_dir = project_root / "frontend" / "docs"

    if not docs_dir.exists():
        logger.error(f"Docs directory not found: {docs_dir}")
        sys.exit(1)

    logger.info(f"Processing docs from: {docs_dir}")

    # Process all markdown files
    processor = MarkdownProcessor(str(docs_dir))
    chunks = processor.process_all_files()

    if not chunks:
        logger.error("No chunks generated - nothing to upload")
        sys.exit(1)

    # Upload to Qdrant
    seed_qdrant(chunks)

    logger.info("=" * 60)
    logger.info("Seeding complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
