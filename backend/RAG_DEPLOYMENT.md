# RAG System Deployment Guide

Complete guide for deploying the Retrieval Augmented Generation (RAG) system for the Physical AI & Humanoid Robotics course.

## 📁 System Architecture

```
backend/
├── rag/
│   ├── ingestion/
│   │   └── document_loader.py      # PDF/Text loading
│   ├── chunking/
│   │   └── text_splitter.py        # Document chunking
│   ├── embeddings/
│   │   └── embedding_generator.py  # OpenAI/HuggingFace embeddings
│   ├── vectordb/
│   │   └── faiss_store.py          # FAISS vector database
│   ├── retrieval/
│   │   └── retriever.py            # Hybrid search + reranking
│   └── pipeline.py                 # Main RAG orchestrator
├── api/routes/
│   └── rag.py                      # FastAPI endpoints
└── data/
    ├── documents/                  # Document storage
    └── vectorstore/                # FAISS index storage

frontend/
└── src/pages/
    └── rag-chat.tsx                # Chat UI
```

## 🚀 Quick Start

### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Create `.env` file from template:
```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Required: OpenAI API Key (for LLM responses)
OPENAI_API_KEY=sk-your-key-here

# Optional: Choose embedding provider
EMBEDDING_PROVIDER=huggingface  # or "openai"

# If using OpenAI embeddings (faster, requires API key)
# EMBEDDING_PROVIDER=openai
# EMBEDDING_MODEL=text-embedding-3-small

# Document chunking configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Vector store location
VECTOR_STORE_DIR=data/vectorstore
```

### 3. Initialize RAG System

#### Option A: Using Python Script

```python
# scripts/init_rag.py
from rag.pipeline import RAGPipeline
import os

# Initialize pipeline
pipeline = RAGPipeline(
    embedding_provider=os.getenv("EMBEDDING_PROVIDER", "huggingface"),
    chunk_size=1000,
    chunk_overlap=200
)

# Ingest documents
stats = pipeline.ingest_documents("data/documents")
print(f"Indexed {stats['chunks_created']} chunks from {stats['documents_loaded']} documents")

# Test query
result = pipeline.chat("What is ROS 2?", k=3)
print(f"Answer: {result['answer']}")
```

Run:
```bash
python scripts/init_rag.py
```

#### Option B: Using API Endpoints

Start the server:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Then use the API:
```bash
# Check status
curl http://localhost:8000/api/rag/status

# Upload document
curl -X POST http://localhost:8000/api/rag/ingest/upload \
  -F "file=@path/to/document.pdf"

# Query
curl -X POST http://localhost:8000/api/rag/chat/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is ROS 2?", "k": 4}'
```

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies (if not done)
npm install

# Start development server
npm start
```

Visit: `http://localhost:3000/hackathon-book/rag-chat`

## 📚 Document Ingestion Methods

### Method 1: Upload via Frontend UI

1. Go to `/rag-chat` page
2. Click "Upload Document" button
3. Select PDF, TXT, or MD file
4. Wait for processing completion

### Method 2: API Upload

```python
import requests

url = "http://localhost:8000/api/rag/ingest/upload"
files = {"file": open("document.pdf", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

### Method 3: Batch Directory Upload

```python
import requests

url = "http://localhost:8000/api/rag/ingest/directory"
data = {
    "directory_path": "data/documents",
    "file_types": [".pdf", ".txt", ".md"]
}
response = requests.post(url, json=data)
print(response.json())
```

## 🔧 Configuration Options

### Embedding Providers

#### HuggingFace (Free, Local)
```env
EMBEDDING_PROVIDER=huggingface
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

**Pros:**
- Free
- Runs locally
- No API key needed
- Good for testing

**Cons:**
- Slower than OpenAI
- Requires more RAM

#### OpenAI (Paid, Cloud)
```env
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
```

**Pros:**
- Fast
- High quality embeddings
- Scalable

**Cons:**
- Requires API key
- Costs money ($0.00002/1K tokens)

### Chunking Strategy

```env
# Small chunks (better precision, more vectors)
CHUNK_SIZE=500
CHUNK_OVERLAP=100

# Medium chunks (balanced)
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Large chunks (more context, fewer vectors)
CHUNK_SIZE=2000
CHUNK_OVERLAP=400
```

## 🎯 API Reference

### POST `/api/rag/chat/query`

Query the RAG system.

**Request:**
```json
{
  "question": "What is ROS 2?",
  "k": 4,
  "model": "gpt-3.5-turbo"
}
```

**Response:**
```json
{
  "question": "What is ROS 2?",
  "answer": "ROS 2 is the second generation...",
  "sources": [
    {
      "content": "ROS 2 is a robotics middleware...",
      "source": "module-01-ros2/intro.md",
      "metadata": {...}
    }
  ],
  "num_sources": 4
}
```

### POST `/api/rag/ingest/upload`

Upload single document.

**Request:** `multipart/form-data` with `file` field

**Response:**
```json
{
  "status": "success",
  "documents_loaded": 1,
  "chunks_created": 25,
  "avg_chunk_size": 950.4,
  "vectorstore_total_vectors": 125
}
```

### GET `/api/rag/status`

Get RAG system status.

**Response:**
```json
{
  "is_initialized": true,
  "vectorstore_stats": {
    "status": "initialized",
    "total_vectors": 125,
    "dimension": 384
  }
}
```

## 🚢 Production Deployment

### 1. Using Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directories
RUN mkdir -p data/documents data/vectorstore

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t rag-backend .
docker run -p 8000:8000 -v $(pwd)/data:/app/data --env-file .env rag-backend
```

### 2. Deploy to Render

```yaml
# render.yaml
services:
  - type: web
    name: rag-backend
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: OPENAI_API_KEY
        sync: false
      - key: EMBEDDING_PROVIDER
        value: huggingface
```

### 3. Deploy to Railway

1. Create new project
2. Connect GitHub repo
3. Add environment variables
4. Deploy automatically

## 🧪 Testing

```bash
# Run tests
cd backend
pytest tests/

# Test specific module
pytest tests/test_rag.py
```

Create test file `tests/test_rag.py`:

```python
from rag.pipeline import RAGPipeline
import pytest

def test_document_ingestion():
    pipeline = RAGPipeline(embedding_provider="huggingface")

    # Create test document
    test_doc_path = "tests/fixtures/test.txt"
    with open(test_doc_path, "w") as f:
        f.write("This is a test document about ROS 2.")

    # Ingest
    stats = pipeline.ingest_documents(test_doc_path)

    assert stats["documents_loaded"] > 0
    assert stats["chunks_created"] > 0

def test_query():
    pipeline = RAGPipeline(embedding_provider="huggingface")
    pipeline.load_existing()

    result = pipeline.query("test question", k=2)

    assert "query" in result
    assert "documents" in result
    assert len(result["documents"]) <= 2
```

## 🔍 Monitoring & Debugging

### View Logs

```bash
# Backend logs
tail -f backend/logs/app.log

# Check RAG pipeline
python -c "from rag.pipeline import RAGPipeline; p = RAGPipeline(); p.load_existing(); print(p.vectorstore.get_stats())"
```

### Common Issues

**Issue: "Vectorstore not initialized"**
```bash
# Solution: Ingest documents first
curl -X POST http://localhost:8000/api/rag/ingest/directory \
  -H "Content-Type: application/json" \
  -d '{"directory_path": "data/documents"}'
```

**Issue: "OPENAI_API_KEY not set"**
```bash
# Solution: Add to .env
echo "OPENAI_API_KEY=sk-..." >> .env
```

**Issue: "Out of memory with HuggingFace embeddings"**
```bash
# Solution: Use smaller model or switch to OpenAI
export EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

## 📊 Performance Optimization

### 1. Cache Embeddings
```python
from rag.embeddings.embedding_generator import EmbeddingCache

cache = EmbeddingCache()
# Embeddings are cached automatically
```

### 2. Use GPU (if available)
```python
# In embedding_generator.py, modify:
self.embeddings = HuggingFaceEmbeddings(
    model_name=self.model_name,
    model_kwargs={'device': 'cuda'},  # Use GPU
    encode_kwargs={'normalize_embeddings': True}
)
```

### 3. Optimize Chunk Size
- Smaller chunks (500): Better precision, slower indexing
- Larger chunks (2000): Faster indexing, more context

## 🎓 Best Practices

1. **Start with HuggingFace** for testing (free, no API key)
2. **Upgrade to OpenAI** for production (better quality)
3. **Index incrementally** - upload documents as needed
4. **Monitor vector count** - keep under 100K for FAISS efficiency
5. **Backup vectorstore** regularly
```bash
tar -czf vectorstore_backup.tar.gz data/vectorstore/
```

## 📝 Next Steps

1. ✅ Setup environment variables
2. ✅ Install dependencies
3. ✅ Ingest initial documents
4. ✅ Test queries via API
5. ✅ Deploy to production

## 🆘 Support

- Documentation: `/docs` endpoint
- API Reference: `/docs` (Swagger UI)
- Issues: GitHub repository

---

**Congratulations!** Your RAG system is now ready to provide intelligent, context-aware responses from your document collection. 🎉
