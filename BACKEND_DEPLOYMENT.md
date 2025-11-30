# Backend Deployment Guide - Render.com

## Quick Deploy to Render

### Option 1: One-Click Deploy (Recommended)
1. Visit: https://render.com
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository: `Asmayaseen/hackathon-book`
4. Render will automatically detect `render.yaml`
5. Add environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `QDRANT_URL`: Your Qdrant cloud URL
   - `QDRANT_API_KEY`: Your Qdrant API key
   - `DATABASE_URL`: Your Neon PostgreSQL URL
   - `SECRET_KEY`: Random secret key for JWT
6. Click "Apply" to deploy

### Option 2: Manual Web Service
1. Go to Render Dashboard → New + → Web Service
2. Connect repository: `Asmayaseen/hackathon-book`
3. Configure:
   - **Name**: hackathon-book-api
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables (same as above)
5. Click "Create Web Service"

## Environment Variables

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-v1SwO...
OPENAI_MODEL=gpt-4o

# Qdrant Vector Database
QDRANT_URL=https://62b19621-b26c-4520-9bfc-534b3b53dbc9.eu-central-1-0.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# PostgreSQL Database (Neon)
DATABASE_URL=postgresql://neondb_owner:npg_eUjrQv5Ew4OM@ep-royal-shape-a58lxe7n.us-east-2.aws.neon.tech/neondb?sslmode=require

# Authentication
SECRET_KEY=&9kfhf@h4r%wn9pe$-@0#jw7xalma#2)to&tl$#xgi$1+ig=na

# CORS (Frontend URLs)
ALLOWED_ORIGINS=https://asmayaseen.github.io,http://localhost:3000
```

## After Deployment

### 1. Test API Endpoints
Once deployed, your API will be at: `https://hackathon-book-api.onrender.com`

Test health check:
```bash
curl https://hackathon-book-api.onrender.com/health
```

### 2. Seed Qdrant Database
After deployment, run the seed script to populate vector database:

```bash
# SSH into Render service or run locally
cd backend
python scripts/seed_embeddings.py
```

This will:
- Read all markdown files from `frontend/docs/`
- Chunk them into 512-token segments
- Generate embeddings with OpenAI
- Upload to Qdrant collection `textbook_embeddings`

### 3. Update Frontend
Update chatbot service URL in `frontend/src/services/chatService.ts`:

```typescript
const API_BASE_URL = process.env.NODE_ENV === 'production'
  ? 'https://hackathon-book-api.onrender.com/api'
  : 'http://localhost:8000/api';
```

### 4. Test RAG Chatbot
Visit your site and test the chatbot:
- https://asmayaseen.github.io/hackathon-book/
- Ask questions about ROS 2, Gazebo, NVIDIA Isaac, etc.
- Verify <3s response time
- Check source citations

## API Endpoints

**Base URL**: `https://hackathon-book-api.onrender.com`

### RAG Chatbot (+50 points)
- `POST /api/chat/query` - Ask question, get AI answer with sources
- `GET /api/chat/health` - Check RAG system status

### Authentication (+50 points)
- `POST /api/auth/signup` - User registration
- `POST /api/auth/signin` - User login
- `GET /api/auth/me` - Get current user

### Translation (+50 points)
- `POST /api/translate/urdu` - Translate content to Urdu

## Monitoring

- View logs: Render Dashboard → Service → Logs
- Check metrics: Render Dashboard → Service → Metrics
- Set up alerts: Render Dashboard → Settings → Notifications

## Troubleshooting

### Build Fails
- Check `requirements.txt` syntax
- Verify Python version (3.11)
- Review build logs in Render dashboard

### Runtime Errors
- Check environment variables are set
- Verify API keys are valid
- Check service logs for details

### Slow Responses
- Upgrade to paid Render plan (free tier spins down after 15min)
- Optimize embedding search (reduce limit from 5 to 3)
- Cache frequently asked questions

## Cost Optimization

- **Free Tier**: Good for development/testing
  - Spins down after 15min inactivity
  - 750 hours/month free

- **Starter Plan** ($7/month): Recommended for hackathon
  - Always-on service
  - Faster response times
  - Better for judging/demo

## Support

- Render Docs: https://render.com/docs
- FastAPI Docs: https://hackathon-book-api.onrender.com/docs
- Issues: https://github.com/Asmayaseen/hackathon-book/issues
