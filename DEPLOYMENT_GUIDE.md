# 🚀 Deployment Guide - Host for Your Friend

## Architecture

```
Frontend (Next.js) → Vercel (Free)
Backend (Flask API) → Railway (Free)
Database (PostgreSQL) → Railway (Free)
```

## Option 1: Simple Deployment (Recommended)

### Step 1: Deploy Backend to Railway

1. **Create Railway Account**
   - Go to https://railway.app
   - Sign up with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your repository

3. **Add PostgreSQL Database**
   - Click "New" → "Database" → "PostgreSQL"
   - Railway will create a database automatically

4. **Configure Backend**
   - Railway will auto-detect Python
   - Set environment variables (see below)

### Step 2: Deploy Frontend to Vercel

1. **Create Vercel Account**
   - Go to https://vercel.com
   - Sign up with GitHub

2. **Import Project**
   - Click "New Project"
   - Import your GitHub repository
   - Select the `frontend` folder as root directory

3. **Configure**
   - Framework: Next.js (auto-detected)
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `.next`

4. **Add Environment Variable**
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.railway.app
   ```

5. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes

## Option 2: All-in-One (Simpler but Limited)

Deploy everything to Railway:
- Backend + Frontend + Database on Railway
- No Vercel needed
- Easier setup but less optimized

## Important Notes

### ⚠️ Chrome/Selenium Issue

**Problem:** Serverless platforms (Vercel, Railway) can't run Chrome easily.

**Solutions:**

1. **Use Playwright (Recommended)**
   - Replace Selenium with Playwright
   - Works on serverless platforms
   - I can help you convert the code

2. **Use Scraping API Service**
   - ScrapingBee, Bright Data, etc.
   - Costs money but reliable

3. **Run Scraper Locally**
   - Keep scraper on your computer
   - Only deploy the dashboard
   - Your friend views data, you scrape

## Quick Setup Files

I'll create the necessary files for deployment...
