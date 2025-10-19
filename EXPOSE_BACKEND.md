# 🌐 Expose Your Local Backend to the Internet

## Problem
- Your backend runs on `http://127.0.0.1:5001` (only accessible on your PC)
- Your friend can access the Vercel frontend but can't reach your backend
- You need a public URL that points to your local backend

## ✅ Solution: Use ngrok

ngrok creates a secure tunnel from a public URL to your local server.

### Step 1: Install ngrok

**Option A: Download from website**
1. Go to https://ngrok.com/download
2. Download for Windows
3. Extract the zip file
4. Move `ngrok.exe` to your project folder

**Option B: Use Chocolatey (if you have it)**
```bash
choco install ngrok
```

### Step 2: Sign Up (Free)
1. Go to https://dashboard.ngrok.com/signup
2. Sign up for free account
3. Copy your authtoken from https://dashboard.ngrok.com/get-started/your-authtoken

### Step 3: Configure ngrok
```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

### Step 4: Start Your Backend
```bash
python api.py
```
(Keep this running)

### Step 5: Start ngrok (New Terminal)
```bash
ngrok http 5001
```

You'll see output like:
```
Session Status                online
Account                       your@email.com
Version                       3.x.x
Region                        United States (us)
Forwarding                    https://abc123.ngrok-free.app -> http://localhost:5001
```

### Step 6: Copy the Public URL

Copy the `https://abc123.ngrok-free.app` URL

### Step 7: Update Vercel Environment Variable

1. Go to https://vercel.com/dashboard
2. Click on your project
3. Go to **Settings** → **Environment Variables**
4. Update `NEXT_PUBLIC_API_URL`:
   ```
   NEXT_PUBLIC_API_URL = https://abc123.ngrok-free.app
   ```
5. Click **Save**
6. Go to **Deployments** → **Redeploy**

### Step 8: Done! 🎉

Now your friend can:
- Open `https://your-app.vercel.app`
- See all the data from your backend
- Everything works!

## 🔄 Daily Workflow

**Every time you want to share:**

1. **Start Backend:**
   ```bash
   python api.py
   ```

2. **Start ngrok (New Terminal):**
   ```bash
   ngrok http 5001
   ```

3. **Copy the new URL** (ngrok gives you a new URL each time on free plan)

4. **Update Vercel env var** with the new URL

5. **Redeploy** on Vercel

## 💡 Alternative: ngrok Static Domain (Paid)

If you don't want to update the URL every time:

1. Upgrade to ngrok paid plan ($8/month)
2. Get a static domain like `your-app.ngrok-free.app`
3. Set it once in Vercel
4. Never update again!

## 🔒 Security Notes

**ngrok is safe because:**
- ✅ Encrypted HTTPS tunnel
- ✅ Only you control when it's running
- ✅ You can see all requests in ngrok dashboard
- ✅ Can add password protection

**To add password protection:**
```bash
ngrok http 5001 --basic-auth="username:password"
```

Then update your frontend to include auth headers.

## 🎯 Alternative Solutions

### Option 1: Deploy Backend to Railway (Better for production)

1. Create Railway account
2. Deploy backend to Railway
3. Get permanent URL
4. No need to keep your PC running

### Option 2: Use Cloudflare Tunnel (Free, permanent)

1. Install cloudflared
2. Create tunnel
3. Get permanent URL
4. Free forever!

### Option 3: Use localtunnel (Quick & Free)

```bash
npm install -g localtunnel
lt --port 5001
```

Gets you a public URL instantly!

## 📋 Quick Commands

```bash
# Terminal 1: Backend
python api.py

# Terminal 2: ngrok
ngrok http 5001

# Terminal 3: Frontend (local testing)
cd frontend
npm run dev
```

---

**Recommended: Start with ngrok, then move to Railway for production!**
