# 🚀 Quick Deployment Guide

## Current Status ✅

✅ All bugs fixed and code committed locally
✅ Ready to deploy to GitHub + Vercel

---

## Step 1️⃣: Push to GitHub (2 minutes)

```bash
cd /mnt/d/hackathon-robotic/hackathon-book

# Push your changes
git push origin 002-ui-enhancements

# Merge to main
git checkout main
git merge 002-ui-enhancements
git push origin main
```

**Note**: You'll need your GitHub Personal Access Token. Get it here:
👉 https://github.com/settings/tokens

---

## Step 2️⃣: Deploy Frontend to Vercel (5 minutes)

### Quick Deploy via CLI:
```bash
# Install Vercel CLI
npm install -g vercel

# Go to frontend
cd frontend

# Login and deploy
vercel login
vercel --prod
```

### Or via Dashboard:
1. Go to: **https://vercel.com/new**
2. Import: `https://github.com/Asmayaseen/hackathon-book`
3. Settings:
   - **Root Directory**: `frontend`
   - **Framework**: Docusaurus
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`
4. Click **Deploy**

---

## Step 3️⃣: Deploy Backend to Render (10 minutes)

1. Go to: **https://render.com/**
2. Click **New** → **Web Service**
3. Connect GitHub → Select `hackathon-book`
4. Settings:
   - **Name**: `hackathon-book-api`
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add **Environment Variables** (from `backend/.env`):
   ```
   OPENAI_API_KEY=sk-proj-krvx0mrK1iTjiJYTNYq9zIc1wFGV...
   QDRANT_URL=https://62b19621-b26c-4520-9bfc...
   QDRANT_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   DATABASE_URL=sqlite:///./hackathon.db
   SECRET_KEY=hackathon-secret-key-for-jwt-tokens-min-32-chars
   ```
6. Click **Create Web Service**

---

## Step 4️⃣: Seed Database (5 minutes)

After backend is deployed:

1. Go to Render Dashboard → Your Service → **Shell**
2. Run:
   ```bash
   python scripts/seed_embeddings.py
   ```

---

## Step 5️⃣: Update API URL (2 minutes)

Update frontend to use your Render backend URL:

**Edit** `frontend/src/theme/Navbar/index.tsx` (lines 37-39):
```typescript
const API_URL = process.env.NODE_ENV === 'production'
  ? 'https://hackathon-book-api.onrender.com/api'  // ← Your Render URL
  : 'http://localhost:8000/api';
```

**Edit** `frontend/src/services/chatService.ts` (line 12):
```typescript
const API_BASE_URL = 'https://hackathon-book-api.onrender.com/api';
```

**Commit and push:**
```bash
git add .
git commit -m "Update production API URL"
git push origin main
```

Vercel will auto-deploy the changes.

---

## ✅ Done!

Your app is now live at:
- **Frontend**: `https://hackathon-book-<id>.vercel.app`
- **Backend**: `https://hackathon-book-api.onrender.com`

---

## 🧪 Test Your Deployment

```bash
# Test backend health
curl https://hackathon-book-api.onrender.com/health

# Test frontend
# Open in browser: https://hackathon-book-<id>.vercel.app
```

---

## 📝 Summary of Fixes Applied

1. ✅ **Fixed Search Button** - Removed invalid Algolia config
2. ✅ **Fixed Translation** - Changed `os.time()` to `time.time()`
3. ✅ **All Dependencies** - Verified and working
4. ✅ **Content** - 35 markdown files ready
5. ✅ **Backend** - RAG chatbot, auth, translation ready

---

**Need help?** See full guide: `DEPLOYMENT_INSTRUCTIONS.md`
