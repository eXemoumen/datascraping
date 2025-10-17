#!/bin/bash

# 🚀 Deploy EspaceAgro Scraper to Vercel
# Run this script to deploy everything

echo "🚀 Starting deployment process..."

# Step 1: Check if git is initialized
if [ ! -d .git ]; then
    echo "📦 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit - EspaceAgro Scraper"
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

# Step 2: Check if remote is set
if ! git remote | grep -q origin; then
    echo "⚠️  No git remote found"
    echo "Please add your GitHub repository:"
    echo "git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
    echo "git push -u origin main"
    exit 1
else
    echo "✅ Git remote configured"
fi

# Step 3: Push to GitHub
echo "📤 Pushing to GitHub..."
git add .
git commit -m "Prepare for deployment" || echo "No changes to commit"
git push origin main
echo "✅ Pushed to GitHub"

# Step 4: Install Vercel CLI (optional)
echo "🔧 Checking Vercel CLI..."
if ! command -v vercel &> /dev/null; then
    echo "Installing Vercel CLI..."
    npm install -g vercel
    echo "✅ Vercel CLI installed"
else
    echo "✅ Vercel CLI already installed"
fi

# Step 5: Deploy to Vercel
echo "🚀 Deploying to Vercel..."
cd frontend
vercel --prod

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "1. Go to https://vercel.com/dashboard"
echo "2. Find your project"
echo "3. Add environment variable:"
echo "   NEXT_PUBLIC_API_URL = http://localhost:5001"
echo "4. Redeploy"
echo ""
echo "🌐 Your app will be live at: https://your-app.vercel.app"
echo ""
