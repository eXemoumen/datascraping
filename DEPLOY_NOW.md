# 🚀 Deploy to Vercel in 5 Minutes

## Quick Deploy (Easiest Way)

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### 2. Deploy to Vercel

1. Go to **https://vercel.com**
2. Click **"Sign Up"** (use GitHub)
3. Click **"Add New..."** → **"Project"**
4. Select your repository
5. Configure:
   - **Root Directory:** `frontend`
   - **Framework:** Next.js (auto-detected)
   - Click **"Deploy"**

### 3. Done! 🎉

Your app is live at: `https://your-app.vercel.app`

## ⚙️ Configuration

After deployment, add environment variable:

1. Go to your project on Vercel
2. Click **"Settings"** → **"Environment Variables"**
3. Add:
   ```
   NEXT_PUBLIC_API_URL = http://localhost:5001
   ```
4. Click **"Save"**
5. Redeploy

## 🎯 How It Works

**For You (Local):**
- Run scraper: `python espaceagro_scraper.py`
- Data saves to database
- Run backend: `python api.py`

**For Your Friend (Online):**
- Opens: `https://your-app.vercel.app`
- Views all data
- Can check/uncheck items
- Can search and filter
- **Cannot scrape** (button hidden in production)

## 🔄 Update Data

When you scrape new data:
1. Run scraper locally
2. Data saves to database
3. Your friend sees updates when they refresh

## 💡 Want Real-Time Sync?

Use Railway for backend:
1. Deploy backend to Railway (free)
2. Get Railway URL
3. Update Vercel env var to Railway URL
4. Now data syncs automatically!

See `VERCEL_DEPLOYMENT.md` for full guide.

---

**That's it!** Your friend can now access the dashboard online! 🎉
