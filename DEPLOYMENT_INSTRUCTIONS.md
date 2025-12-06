# Deployment Instructions

## ✅ Changes Committed Locally

I've successfully committed the following fixes to branch `002-ui-enhancements`:
- Fixed search button error (removed invalid Algolia configuration)
- Fixed translation route error (`os.time()` → `time.time()`)

**Commit:** `8e7a1ae`

---

## 📤 Step 1: Push to GitHub

Since git authentication is required, please run one of these commands:

### Option A: Using HTTPS (requires Personal Access Token)
```bash
cd /mnt/d/hackathon-robotic/hackathon-book
git push origin 002-ui-enhancements
```

Then enter your GitHub username and **Personal Access Token** (not password).

**Don't have a token?** Create one at: https://github.com/settings/tokens
- Click "Generate new token (classic)"
- Select scope: `repo`
- Copy the token and use it as your password

### Option B: Using SSH (if SSH keys configured)
```bash
# First, change remote to SSH
git remote set-url origin git@github.com:Asmayaseen/hackathon-book.git

# Then push
git push origin 002-ui-enhancements
```

### After Pushing
Merge your branch into `main`:
```bash
git checkout main
git merge 002-ui-enhancements
git push origin main
```

---

## 🚀 Step 2: Deploy Frontend to Vercel

### Method 1: Using Vercel CLI (Recommended)

1. **Install Vercel CLI**:
```bash
npm install -g vercel
```

2. **Navigate to Frontend**:
```bash
cd /mnt/d/hackathon-robotic/hackathon-book/frontend
```

3. **Login to Vercel**:
```bash
vercel login
```

4. **Deploy**:
```bash
# For preview deployment
vercel

# For production deployment
vercel --prod
```

5. **Configure Build Settings** (when prompted):
   - Framework Preset: `Docusaurus`
   - Build Command: `npm run build`
   - Output Directory: `build`
   - Install Command: `npm install`

### Method 2: Using Vercel Dashboard

1. **Go to**: https://vercel.com/new

2. **Import Git Repository**:
   - Click "Import Project"
   - Select "Import Git Repository"
   - Enter: `https://github.com/Asmayaseen/hackathon-book`
   - Click "Continue"

3. **Configure Project**:
   - **Project Name**: `hackathon-book`
   - **Framework Preset**: `Docusaurus`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`
   - **Install Command**: `npm install`

4. **Environment Variables** (if needed):
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com/api
   ```

5. **Click "Deploy"**

6. **Wait for Deployment** (usually 2-3 minutes)

### Update vercel.json (Already exists)
The project already has a `vercel.json` configuration:
```json
{
  "buildCommand": "cd frontend && npm run build",
  "outputDirectory": "frontend/build",
  "installCommand": "cd frontend && npm install",
  "framework": "docusaurus"
}
```

---

## 🔧 Step 3: Deploy Backend to Render

### Option 1: Using Render Dashboard

1. **Go to**: https://render.com/

2. **Create New Web Service**:
   - Click "New" → "Web Service"
   - Connect your GitHub account
   - Select repository: `Asmayaseen/hackathon-book`
   - Click "Connect"

3. **Configure Service**:
   - **Name**: `hackathon-book-api`
   - **Region**: Choose closest to your users
   - **Branch**: `main` (or `002-ui-enhancements`)
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Environment Variables**:
   Add these from your `backend/.env` file:
   ```
   OPENAI_API_KEY=sk-proj-krvx0mrK1iTjiJYTNYq9zIc1wFGV9MdR-...
   OPENAI_MODEL=gpt-4o
   QDRANT_URL=https://62b19621-b26c-4520-9bfc-534b3b53dbc9.eu-central-1-0.aws.cloud.qdrant.io
   QDRANT_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   DATABASE_URL=sqlite:///./hackathon.db
   SECRET_KEY=hackathon-secret-key-for-jwt-tokens-min-32-chars
   ALLOWED_ORIGINS=https://your-vercel-url.vercel.app
   ```

5. **Plan**: Select "Free" tier

6. **Click "Create Web Service"**

7. **Wait for Deployment** (5-10 minutes)

### After Backend Deployment

8. **Seed Qdrant Database**:
   - Go to Render dashboard → Your service → "Shell"
   - Run: `python scripts/seed_embeddings.py`

9. **Test Health Check**:
   ```bash
   curl https://your-backend-url.onrender.com/health
   ```

---

## 🔗 Step 4: Connect Frontend to Backend

Update the frontend to use your deployed backend URL:

1. **Edit** `frontend/src/theme/Navbar/index.tsx`:
```typescript
const API_URL = process.env.NODE_ENV === 'production'
  ? 'https://hackathon-book-api.onrender.com/api'
  : 'http://localhost:8000/api';
```

2. **Edit** `frontend/src/services/chatService.ts` (if needed):
```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ||
  'https://hackathon-book-api.onrender.com/api';
```

3. **Commit and Push**:
```bash
git add .
git commit -m "Update API URL for production"
git push origin main
```

4. **Vercel will auto-deploy** the updated frontend

---

## 📋 Deployment Checklist

- [ ] Push code to GitHub
- [ ] Deploy frontend to Vercel
- [ ] Deploy backend to Render
- [ ] Add environment variables to Render
- [ ] Seed embeddings to Qdrant
- [ ] Update frontend API URL
- [ ] Test all features:
  - [ ] RAG Chatbot
  - [ ] Urdu Translation
  - [ ] Authentication
  - [ ] Personalization
  - [ ] All pages load correctly

---

## 🌐 Expected URLs

After deployment, you'll have:

- **Frontend (Vercel)**: `https://hackathon-book-<random>.vercel.app`
- **Backend (Render)**: `https://hackathon-book-api.onrender.com`
- **Docs**: `https://hackathon-book-<random>.vercel.app/docs/intro`

You can configure custom domains later in Vercel and Render dashboards.

---

## 🐛 Troubleshooting

### Frontend Build Fails
```bash
# Clear cache and rebuild
cd frontend
rm -rf node_modules .docusaurus
npm install
npm run build
```

### Backend Won't Start
- Check environment variables in Render dashboard
- View logs: Render Dashboard → Your Service → Logs
- Verify `requirements.txt` has all dependencies

### CORS Errors
Update `ALLOWED_ORIGINS` in backend `.env`:
```
ALLOWED_ORIGINS=https://your-vercel-url.vercel.app,http://localhost:3000
```

### Chatbot Not Working
1. Verify Qdrant is seeded: Check collection has vectors
2. Check OpenAI API key is valid
3. Check backend `/health` endpoint

---

## 📞 Support

If you encounter issues:
1. Check deployment logs in Vercel/Render dashboards
2. Review this guide step by step
3. Verify all environment variables are set correctly

---

**Built with ⚡ Claude Code**
