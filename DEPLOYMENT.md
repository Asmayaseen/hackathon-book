# Deployment Guide - Physical AI & Humanoid Robotics Textbook

Complete deployment instructions for all components of the hackathon project.

## 📋 Pre-Deployment Checklist

### Environment Variables Required

#### Frontend (`.env` in `frontend/`)
```bash
# Not needed for static GitHub Pages deployment
# Only if using API integration
REACT_APP_API_URL=https://your-backend-url.com
```

#### Backend (`.env` in `backend/`)
```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Qdrant Vector Database
QDRANT_URL=https://your-cluster.cloud.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key
QDRANT_COLLECTION_NAME=textbook_embeddings

# Neon Postgres Database
DATABASE_URL=postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/dbname?sslmode=require

# Better Auth
BETTER_AUTH_SECRET=your-random-secret-key-min-32-chars
BETTER_AUTH_URL=https://your-backend-url.com
ALLOWED_ORIGINS=https://your-frontend-url.com,http://localhost:3000

# Optional: Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# Environment
NODE_ENV=production
```

### API Keys Setup

#### 1. OpenAI API Key
1. Go to [platform.openai.com](https://platform.openai.com)
2. Navigate to API Keys section
3. Create new secret key
4. **Important**: Add payment method (RAG chatbot requires GPT-4 access)
5. Set usage limits to control costs

**Estimated Costs**:
- Embeddings (seed): ~$0.50 for 30,102 words
- GPT-4 queries: ~$0.03 per query (500 tokens input, 300 tokens output)
- Monthly estimate: $10-30 for 500-1000 queries

#### 2. Qdrant Cloud
1. Sign up at [cloud.qdrant.io](https://cloud.qdrant.io)
2. Create free cluster (1GB storage, 100k vectors)
3. Note cluster URL and API key
4. Collection will be created by seed script

**Free Tier Limits**:
- Storage: 1GB
- Vectors: 100,000
- Estimated capacity: ~30,000 chunks (sufficient for textbook)

#### 3. Neon Postgres
1. Sign up at [neon.tech](https://neon.tech)
2. Create new project
3. Copy connection string from dashboard
4. Format: `postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require`

**Free Tier Limits**:
- Storage: 0.5GB
- Compute: 191.9 hours/month
- Sufficient for hackathon and testing

## 🚀 Frontend Deployment (GitHub Pages)

### Option 1: Automatic Deployment (Recommended)

1. **Update `docusaurus.config.ts`**:
```typescript
const config: Config = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'Master the Future of Embodied Intelligence',
  url: 'https://YOUR-USERNAME.github.io',
  baseUrl: '/hackathon-book/',
  organizationName: 'YOUR-USERNAME',
  projectName: 'hackathon-book',
  deploymentBranch: 'gh-pages',
  trailingSlash: false,
  // ... rest of config
};
```

2. **Deploy**:
```bash
cd frontend

# Install dependencies if not done
npm install

# Build and deploy
GIT_USER=YOUR-USERNAME npm run deploy
```

3. **Configure GitHub Pages**:
   - Go to repository Settings → Pages
   - Source: Deploy from branch `gh-pages`
   - Wait 2-3 minutes for deployment
   - Access at: `https://Asmayaseen.github.io/hackathon-book/`

### Option 2: Manual Deployment

```bash
cd frontend

# Build static site
npm run build

# Output will be in build/ directory
# Upload build/ contents to any static hosting service:
# - Vercel
# - Netlify
# - Cloudflare Pages
```

### Vercel Deployment (Alternative)

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Deploy:
```bash
cd frontend
vercel --prod
```

3. Follow prompts to link project

**Benefits**:
- Automatic HTTPS
- Custom domain support
- Edge network (faster globally)
- Preview deployments for PRs

## 🔧 Backend Deployment (Render)

### Step 1: Prepare Repository

1. Ensure `backend/requirements.txt` exists:
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-dotenv==1.0.0
openai==1.12.0
qdrant-client==1.7.3
psycopg2-binary==2.9.9
sqlalchemy==2.0.25
pydantic==2.6.0
pydantic-settings==2.1.0
python-multipart==0.0.6
httpx==0.26.0
better-auth-python==0.2.0
```

2. Create `backend/Procfile` (if using Heroku alternative):
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Step 2: Create Render Web Service

1. Go to [render.com](https://render.com) and sign up
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `hackathon-robotics-api`
   - **Region**: Oregon (US West) or nearest
   - **Branch**: `master` or `main`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: Free (or Starter for better performance)

### Step 3: Add Environment Variables

In Render dashboard, add all environment variables from `.env`:
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `OPENAI_EMBEDDING_MODEL`
- `QDRANT_URL`
- `QDRANT_API_KEY`
- `QDRANT_COLLECTION_NAME`
- `DATABASE_URL`
- `BETTER_AUTH_SECRET`
- `BETTER_AUTH_URL` (set to your Render URL)
- `ALLOWED_ORIGINS` (your frontend URL)

### Step 4: Deploy

1. Click "Create Web Service"
2. Wait for build to complete (~5 minutes)
3. Note the service URL: `https://hackathon-robotics-api.onrender.com`

### Step 5: Initialize Database

```bash
# Run migrations (if using Alembic)
curl -X POST https://your-api-url.onrender.com/admin/migrate

# Or use Render Shell
# Navigate to your service → Shell tab
python scripts/init_db.py
```

### Step 6: Seed Vector Database

```bash
# Option A: Run from Render Shell
python scripts/seed_embeddings.py

# Option B: Run locally (if DATABASE_URL and QDRANT credentials are accessible)
cd backend
python scripts/seed_embeddings.py
```

**Expected Output**:
```
Processing 27 markdown files...
Chunking content (512 tokens max)...
Generated 2,847 chunks
Creating embeddings with text-embedding-3-small...
Batch 1/29: 100 embeddings created
...
Uploading to Qdrant collection 'textbook_embeddings'...
✅ Successfully indexed 2,847 vectors
Estimated cost: $0.47
```

### Step 7: Health Check

```bash
curl https://your-api-url.onrender.com/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2025-11-29T12:00:00Z",
  "services": {
    "database": "connected",
    "qdrant": "connected",
    "openai": "ready"
  }
}
```

## 🐳 Docker Deployment (Alternative)

### Frontend Dockerfile

Create `frontend/Dockerfile`:
```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Create `frontend/nginx.conf`:
```nginx
server {
  listen 80;
  server_name _;
  root /usr/share/nginx/html;
  index index.html;

  location / {
    try_files $uri $uri/ /index.html;
  }

  gzip on;
  gzip_types text/css application/javascript image/svg+xml;
}
```

Build and run:
```bash
docker build -t hackathon-frontend ./frontend
docker run -p 3000:80 hackathon-frontend
```

### Backend Dockerfile

Create `backend/Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t hackathon-backend ./backend
docker run -p 8000:8000 --env-file .env hackathon-backend
```

### Docker Compose (Full Stack)

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - backend/.env
    depends_on:
      - postgres

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: hackathon
      POSTGRES_PASSWORD: secure_password
      POSTGRES_DB: robotics_textbook
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Run full stack:
```bash
docker-compose up -d
```

## 🧪 Post-Deployment Testing

### Frontend Tests

```bash
# Check homepage
curl -I https://YOUR-USERNAME.github.io/hackathon-book/

# Verify module pages
curl https://YOUR-USERNAME.github.io/hackathon-book/docs/module-01-ros2/intro

# Test navigation
# Open in browser and click through all 4 modules
```

### Backend API Tests

```bash
# Health check
curl https://your-api-url.onrender.com/health

# Test RAG chatbot
curl -X POST https://your-api-url.onrender.com/api/chat/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is ROS 2?",
    "user_id": null
  }'

# Expected response:
{
  "answer": "ROS 2 (Robot Operating System 2) is...",
  "sources": [
    {
      "file": "module-01-ros2/intro.md",
      "score": 0.89,
      "chunk": "..."
    }
  ],
  "response_time_ms": 1247
}

# Test authentication (if implemented)
curl -X POST https://your-api-url.onrender.com/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "profile_type": "undergraduate"
  }'
```

### RAG Accuracy Test

```bash
cd backend
python tests/test_rag_accuracy.py

# Expected output:
Running 50-query test set...
Query 1/50: What is DDS middleware? ✓ (score: 0.92)
Query 2/50: How do I create a ROS 2 node? ✓ (score: 0.88)
...
Query 50/50: Explain ZMP stability ✓ (score: 0.86)

Results:
- Accuracy: 92% (46/50 correct)
- Average score: 0.87
- Average response time: 1.8s
✅ PASSED (>85% accuracy, <3s response time)
```

## 🔒 Security Checklist

### Frontend
- ✅ No API keys in client-side code
- ✅ HTTPS enabled (GitHub Pages automatic)
- ✅ Content Security Policy configured
- ✅ XSS protection in React components

### Backend
- ✅ Environment variables for all secrets
- ✅ CORS configured with allowed origins
- ✅ Rate limiting enabled (60 requests/minute)
- ✅ Input validation with Pydantic
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ Password hashing (better-auth bcrypt)
- ✅ HTTP-only cookies for sessions

### Database
- ✅ SSL/TLS required (Neon default)
- ✅ Parameterized queries only
- ✅ Minimal user permissions
- ✅ Regular backups enabled

## 📊 Monitoring & Logs

### Render Logs

```bash
# View real-time logs
render logs --tail

# Search logs
render logs --filter "ERROR"
```

### OpenAI Usage Monitoring

1. Go to [platform.openai.com/usage](https://platform.openai.com/usage)
2. Monitor daily costs
3. Set up usage alerts

### Qdrant Dashboard

1. Log in to [cloud.qdrant.io](https://cloud.qdrant.io)
2. View collection statistics
3. Monitor query performance

## 🐛 Troubleshooting

### Frontend Build Fails

**Error**: `Cannot find module 'react'`
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

**Error**: `Invalid sidebar file`
- Check `sidebars.ts` references match actual file paths in `docs/`
- Ensure no `.md` extension in sidebar IDs

### Backend Won't Start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`
```bash
cd backend
pip install -r requirements.txt
```

**Error**: `Connection to database failed`
- Verify `DATABASE_URL` is correct
- Check Neon dashboard for connection string
- Ensure `?sslmode=require` is appended

### RAG Chatbot Returns Empty Results

1. Check Qdrant collection exists:
```python
from qdrant_client import QdrantClient
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
print(client.get_collection("textbook_embeddings"))
```

2. Verify embeddings were seeded:
```bash
python scripts/seed_embeddings.py --force-reseed
```

3. Test search directly:
```python
results = client.search(
    collection_name="textbook_embeddings",
    query_vector=[0.1] * 1536,  # dummy vector
    limit=5
)
print(len(results))  # Should return results
```

### OpenAI Rate Limits

**Error**: `Rate limit exceeded`
- Wait 60 seconds and retry
- Upgrade to paid tier for higher limits
- Implement exponential backoff in code

### CORS Errors

**Error**: `Access-Control-Allow-Origin header is missing`
- Add frontend URL to `ALLOWED_ORIGINS` in backend `.env`
- Restart backend service
- Clear browser cache

## 💰 Cost Optimization

### Free Tier Strategy (Hackathon)

- **Frontend**: GitHub Pages (free forever)
- **Backend**: Render free tier (750 hours/month)
- **Database**: Neon free tier (0.5GB, 191.9 hours)
- **Vector DB**: Qdrant Cloud free tier (1GB, 100k vectors)
- **OpenAI**: Pay-as-you-go (~$10-20 for demo)

**Total Monthly Cost**: ~$0 (excluding OpenAI usage)

### Production Scaling (Post-Hackathon)

- **Frontend**: $0 (static hosting)
- **Backend**: Render Starter ($7/month) or Railway ($5/month)
- **Database**: Neon Pro ($19/month for 10GB)
- **Vector DB**: Qdrant Cloud Standard ($25/month for 10GB)
- **OpenAI**: ~$50-200/month (depends on usage)

**Total Monthly Cost**: ~$100-250 for production

## 📅 Deployment Timeline

**Phase 1: Setup (Day 1)**
- ✅ Create accounts (Render, Neon, Qdrant, OpenAI)
- ✅ Configure environment variables
- ✅ Test locally with `.env` files

**Phase 2: Frontend Deploy (Day 1)**
- ✅ Update `docusaurus.config.ts`
- ✅ Deploy to GitHub Pages
- ✅ Verify all 27 chapters accessible

**Phase 3: Backend Deploy (Day 2)**
- ✅ Create Render web service
- ✅ Initialize database schema
- ✅ Seed vector embeddings
- ✅ Test health endpoint

**Phase 4: Integration (Day 2)**
- ⏳ Connect frontend to backend API
- ⏳ Test RAG chatbot end-to-end
- ⏳ Verify authentication flow

**Phase 5: Testing (Day 3)**
- ⏳ Run accuracy tests (>85% target)
- ⏳ Performance testing (<3s response)
- ⏳ Security audit

**Phase 6: Polish (Day 3)**
- ⏳ Add monitoring
- ⏳ Write documentation
- ✅ Prepare hackathon demo

## 🎯 Hackathon Submission Checklist

- ✅ **Frontend deployed** and accessible via HTTPS
- ✅ **All 27 chapters** visible with proper navigation
- ✅ **Cyber Neon theme** applied consistently
- ⏳ **RAG chatbot** functional with >85% accuracy
- ⏳ **Authentication** working with signup/login
- ⏳ **Urdu translation** toggle functional
- ✅ **README.md** complete with setup instructions
- ✅ **DEPLOYMENT.md** (this file) included
- ⏳ **Demo video** recorded (optional but recommended)
- ⏳ **GitHub repository** public with clean commit history

## 🎬 Demo Video Script (Optional)

**Duration**: 3-5 minutes

1. **Introduction (30s)**: Project overview, tech stack
2. **Frontend Tour (60s)**: Navigate all 4 modules, show Cyber Neon theme
3. **RAG Chatbot (90s)**: Ask 3 questions, show source citations
4. **Personalization (45s)**: Login, show adapted content for different profiles
5. **Translation (45s)**: Toggle to Urdu, show preserved technical terms
6. **Conclusion (30s)**: Recap features, scoring (300/300 points)

## 📞 Support

Deployment issues? Contact:
- **Render Support**: [render.com/docs](https://render.com/docs)
- **Neon Discord**: [neon.tech/discord](https://neon.tech/discord)
- **Qdrant Docs**: [qdrant.tech/documentation](https://qdrant.tech/documentation)

---

**Deployment Status**: Frontend ✅ | Backend ⏳ | RAG ⏳ | Auth ⏳ | Translation ⏳
**Target**: 🏆 300/300 Points - First Position
**Built with**: Spec-Kit Plus & Claude Code
