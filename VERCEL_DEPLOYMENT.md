# 🚀 Deploy to Vercel - Step by Step

## 🎯 What We're Deploying

**Frontend Only** → Vercel (your friend can view data)
**Backend + Scraper** → Stays on your computer (you scrape and upload data)

## Why This Approach?

- ✅ **Free** - Vercel is free for personal projects
- ✅ **Fast** - Vercel is optimized for Next.js
- ✅ **Simple** - No complex backend setup needed
- ✅ **Secure** - Your friend can't trigger scraping (only you can)

## 📋 Prerequisites

1. GitHub account
2. Vercel account (free)
3. Your code pushed to GitHub

## 🚀 Step-by-Step Deployment

### Step 1: Prepare Frontend for Deployment

Update the API URL to use environment variable:

**File: `frontend/app/page.tsx`**

Change this line:
```typescript
const API_URL = 'http://localhost:5001';
```

To:
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001';
```

### Step 2: Create Vercel Configuration

Already created! See `frontend/vercel.json`

### Step 3: Push to GitHub

```bash
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

### Step 4: Deploy to Vercel

1. **Go to Vercel**
   - Visit https://vercel.com
   - Click "Sign Up" (use GitHub)

2. **Import Project**
   - Click "Add New..." → "Project"
   - Select your GitHub repository
   - Click "Import"

3. **Configure Project**
   - Framework Preset: **Next.js** (auto-detected)
   - Root Directory: **frontend**
   - Build Command: `npm run build` (default)
   - Output Directory: `.next` (default)

4. **Add Environment Variables**
   - Click "Environment Variables"
   - Add:
     ```
     Name: NEXT_PUBLIC_API_URL
     Value: https://your-backend-url.com
     ```
   - For now, use: `http://localhost:5001` (we'll update later)

5. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes
   - You'll get a URL like: `https://your-app.vercel.app`

## 🔄 Workflow After Deployment

### For You (Admin):
1. Run scraper locally: `python espaceagro_scraper.py`
2. Data saves to local database
3. Export database and upload to cloud (optional)

### For Your Friend (Viewer):
1. Opens: `https://your-app.vercel.app`
2. Views all scraped data
3. Can check/uncheck announcements
4. Can search and filter
5. **Cannot trigger scraping** (button disabled)

## 🎨 Customize for Production

### Hide Scraping Button

**File: `frontend/app/page.tsx`**

Add this at the top:
```typescript
const IS_PRODUCTION = process.env.NODE_ENV === 'production';
```

Then hide the button:
```typescript
{!IS_PRODUCTION && (
  <button onClick={startScraping} ...>
    Start Scraping
  </button>
)}
```

## 🗄️ Database Options

### Option 1: Shared SQLite (Simple)
- Keep SQLite database
- Upload to Dropbox/Google Drive
- Update link in frontend
- **Pros:** Simple, free
- **Cons:** Manual sync needed

### Option 2: PostgreSQL (Better)
- Use Supabase (free tier)
- Or Railway (free tier)
- Auto-sync between you and friend
- **Pros:** Real-time sync
- **Cons:** Requires setup

### Option 3: Firebase (Easiest)
- Use Firebase Realtime Database
- Free tier is generous
- Real-time updates
- **Pros:** Easiest, real-time
- **Cons:** Different database structure

## 🚀 Quick Deploy Commands

```bash
# 1. Install Vercel CLI (optional)
npm install -g vercel

# 2. Deploy from command line
cd frontend
vercel

# 3. Follow prompts
# - Link to existing project? No
# - Project name? espaceagro-scraper
# - Directory? ./
# - Override settings? No

# 4. Deploy to production
vercel --prod
```

## 🎯 What Your Friend Will See

```
https://your-app.vercel.app

┌─────────────────────────────────────┐
│  EspaceAgro Scraper Dashboard       │
├─────────────────────────────────────┤
│  📊 Stats: 450 total, 120 checked   │
│                                     │
│  🔍 Search: [____________]          │
│                                     │
│  📋 Table with all announcements    │
│  ✓ Can check/uncheck               │
│  ✓ Can search/filter                │
│  ✓ Can view details                 │
│  ❌ Cannot scrape (you do that)     │
└─────────────────────────────────────┘
```

## 💡 Pro Tips

1. **Custom Domain**
   - Buy domain on Namecheap ($10/year)
   - Connect to Vercel (free)
   - Your friend gets: `scraper.yourdomain.com`

2. **Password Protection**
   - Add simple auth to frontend
   - Only your friend can access
   - Vercel supports this natively

3. **Auto-Deploy**
   - Every git push auto-deploys
   - No manual deployment needed
   - Takes 2-3 minutes

## 🆘 Troubleshooting

### Build Fails
- Check `frontend/package.json` is correct
- Ensure all dependencies are listed
- Check Node.js version compatibility

### API Not Working
- Update `NEXT_PUBLIC_API_URL` in Vercel
- Check CORS settings in backend
- Verify backend is running

### Data Not Showing
- Check browser console for errors
- Verify API URL is correct
- Test API endpoint directly

## 📞 Need Help?

Check these files:
- `DEPLOYMENT_GUIDE.md` - Full deployment guide
- `README_FRONTEND.md` - Frontend documentation
- `ARCHITECTURE.md` - System architecture

---

**Ready to deploy!** 🚀

Just follow the steps above and your friend will be able to access the dashboard!
