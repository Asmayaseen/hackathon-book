---
title: Hackathon Book API
emoji: 📚
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
app_port: 8000
---

# Backend API

FastAPI backend with RAG chatbot, auth, and translation.

## Quick Start
```bash
pip install -r requirements.txt
cp .env.example .env
python main.py
```

Docs: http://localhost:8000/docs

## Endpoints
- POST /api/chat/query - RAG chatbot
- POST /api/auth/signup - User signup
- POST /api/translate - Urdu translation
