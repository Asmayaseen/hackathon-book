# 🚀 Railway Deployment - Simple Steps

## Step 1: Railway Account (2 minutes)

1. Open: https://railway.app
2. Click: **"Start a New Project"** ya **"Login"**
3. Click: **"Login with GitHub"**
4. GitHub authorize karein
5. ✅ Done! $5 free credit mil gaya

---

## Step 2: Deploy Project (1 click!)

### Option A: Deploy Button (Easiest!)

Click this button:

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/Asmayaseen/hackathon-book)

### Option B: Manual Deploy

1. Railway Dashboard → **"New Project"**
2. **"Deploy from GitHub repo"**
3. Select: **"Asmayaseen/hackathon-book"**
4. Railway automatically detect karega

---

## Step 3: Environment Variables (Copy-Paste!)

Railway Dashboard mein:

1. Click: **Variables** tab
2. Click: **"New Variable"** ya **"Add Variables"**
3. Neeche diye variables copy karein aur paste karein:

```
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o
QDRANT_URL=
QDRANT_API_KEY=
SECRET_KEY=your-random-32-char-secret-key
DATABASE_URL=sqlite:///./hackathon.db
ALLOWED_ORIGINS=https://hackathon-book-1.vercel.app,*
EMBEDDING_PROVIDER=huggingface
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

4. **IMPORTANT:** Empty values ko fill karein:
   - `OPENAI_API_KEY` - OpenAI se layein (https://platform.openai.com/api-keys)
   - `QDRANT_URL` - Qdrant Cloud se layein (https://cloud.qdrant.io)
   - `QDRANT_API_KEY` - Qdrant Cloud se layein

---

## Step 4: Deploy! (Automatic)

Variables add karte hi automatic deploy ho jayega!

**Wait:** 3-5 minutes

**Success Check:**
- Green ✅ dikhai dega
- URL milega: `https://your-project.up.railway.app`

---

## Step 5: Test API

Browser mein kholein:
```
https://your-railway-url.up.railway.app/
https://your-railway-url.up.railway.app/docs
```

✅ Success Response:
```json
{
  "message": "Physical AI Textbook API",
  "status": "ready"
}
```

---

## 🆘 Help Needed?

### Agar API keys nahi hain:

**OpenAI API Key:**
1. https://platform.openai.com/api-keys
2. "Create new secret key" → Copy

**Qdrant (Free):**
1. https://cloud.qdrant.io
2. "Create Cluster" → Copy URL aur API Key

**SECRET_KEY (Random):**
```
koi-bhi-random-long-string-minimum-32-characters
```

---

## 💰 Cost

- **Free Tier:** $5 credit = 500 hours
- **After free tier:** ~$5/month

---

**Done! Aapka backend live hai! 🎉**
