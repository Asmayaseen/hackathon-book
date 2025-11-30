# 🚀 Deployment Guide

## Quick Deployment Status

- **Frontend**: GitHub Pages ✅
- **Backend**: Vercel (follow instructions below)

---

## 📦 Frontend Deployment (GitHub Pages)

### Automatic Deployment

Every push to `main`/`master` branch automatically deploys to GitHub Pages via GitHub Actions.

### Manual Deployment

```bash
cd frontend
npm run build
npm run deploy
```

**Live URL**: https://asmayaseen.github.io/hackathon-book/

---

## 🔧 Backend Deployment (Vercel)

### Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

### Step 2: Login to Vercel

```bash
vercel login
```

### Step 3: Add Environment Variables

Go to Vercel Dashboard → Your Project → Settings → Environment Variables

Add these secrets:

```
OPENAI_API_KEY = sk-proj-... (your OpenAI API key)
QDRANT_URL = https://... (your Qdrant Cloud URL)
QDRANT_API_KEY = eyJ... (your Qdrant API key)
SECRET_KEY = hackathon-secret-key-for-jwt-tokens-min-32-chars
```

### Step 4: Deploy Backend

```bash
# From project root
vercel --prod
```

**Backend URL**: Will be provided after deployment (e.g., `hackathon-book-api.vercel.app`)

---

## 🔗 Update Frontend API URL

After backend deployment, update the production API URL:

1. Open `frontend/src/pages/signup.tsx`
2. Update line 26:
   ```typescript
   const API_URL = process.env.NODE_ENV === 'production'
     ? 'https://YOUR-VERCEL-URL.vercel.app/api'  // ← Update this
     : 'http://localhost:8000/api';
   ```

3. Same for `signin.tsx`, `ChatWidget.tsx`, `ContentControls.tsx`

---

## 📋 Deployment Checklist

### Before Deploying

- [ ] OpenAI API key added to `backend/.env`
- [ ] Qdrant credentials configured
- [ ] Frontend builds without errors: `cd frontend && npm run build`
- [ ] Backend starts without errors: `cd backend && uvicorn main:app`

### Frontend (GitHub Pages)

- [ ] Repository settings → Pages → Source: GitHub Actions
- [ ] Push to `main` branch
- [ ] Check Actions tab for deployment status
- [ ] Visit: https://asmayaseen.github.io/hackathon-book/

### Backend (Vercel)

- [ ] Vercel CLI installed
- [ ] Environment variables added to Vercel dashboard
- [ ] Run `vercel --prod`
- [ ] Note the deployed URL
- [ ] Update frontend API URLs with Vercel URL
- [ ] Test signup/signin/chatbot

---

## 🧪 Testing Production Deployment

1. **Homepage**: Visit GitHub Pages URL
2. **Sign Up**: Create a new account
3. **Sign In**: Login with created account
4. **Chatbot**: Ask "What is ROS 2?"
5. **Personalization**: Click "Personalize for Me" on any chapter
6. **Translation**: Click "Urdu Translation"

---

## 🔧 Troubleshooting

### Frontend Build Fails

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Backend API 500 Error

- Check Vercel logs: `vercel logs`
- Verify environment variables are set correctly
- Ensure CORS origins include GitHub Pages URL

### CORS Errors

Update `backend/.env`:
```env
ALLOWED_ORIGINS=https://asmayaseen.github.io,https://asmayaseen.github.io/hackathon-book,http://localhost:3000
```

---

## 📊 Deployment Architecture

```
┌─────────────────────────────────────────┐
│  GitHub Pages (Frontend)                │
│  https://asmayaseen.github.io/          │
│  hackathon-book/                        │
└─────────────┬───────────────────────────┘
              │ API Calls
              ↓
┌─────────────────────────────────────────┐
│  Vercel (Backend API)                   │
│  https://hackathon-book-api.vercel.app  │
└─────────────┬───────────────────────────┘
              │
       ┌──────┴──────┬──────────────┐
       ↓             ↓              ↓
┌────────────┐  ┌──────────┐  ┌─────────┐
│ OpenAI API │  │ Qdrant   │  │ SQLite  │
│            │  │ Cloud    │  │ (Vercel)│
└────────────┘  └──────────┘  └─────────┘
```

---

## 🎯 Production URLs

**Frontend**: https://asmayaseen.github.io/hackathon-book/
**Backend**: https://YOUR-PROJECT.vercel.app (after deployment)
**GitHub Repo**: https://github.com/Asmayaseen/hackathon-book

---

## 💡 Next Steps After Deployment

1. Test all features in production
2. Share the live URL: https://asmayaseen.github.io/hackathon-book/
3. Submit to hackathon with both URLs
4. Monitor Vercel logs for any errors

---

**Need Help?** Check the logs:
- **Frontend**: GitHub Actions tab
- **Backend**: `vercel logs` or Vercel Dashboard
