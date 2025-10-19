@echo off
echo ========================================
echo   ngrok Setup for EspaceAgro Backend
echo ========================================
echo.
echo Step 1: Download ngrok
echo Go to: https://ngrok.com/download
echo Download and extract ngrok.exe to this folder
echo.
echo Step 2: Get your authtoken
echo Go to: https://dashboard.ngrok.com/get-started/your-authtoken
echo.
echo Step 3: Configure ngrok
echo Run: ngrok config add-authtoken YOUR_TOKEN
echo.
echo Step 4: Start ngrok
echo Run: ngrok http 5001
echo.
echo Step 5: Copy the public URL (https://xxx.ngrok-free.app)
echo.
echo Step 6: Update Vercel environment variable
echo NEXT_PUBLIC_API_URL = https://xxx.ngrok-free.app
echo.
echo ========================================
pause
