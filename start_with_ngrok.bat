@echo off
echo ========================================
echo   Starting Backend with ngrok
echo ========================================
echo.
echo This will open 2 windows:
echo 1. Backend API (port 5001)
echo 2. ngrok tunnel
echo.
echo After both start, copy the ngrok URL and update Vercel!
echo.
pause

start "Backend API" cmd /k "python api.py"
timeout /t 3 /nobreak >nul
start "ngrok Tunnel" cmd /k "ngrok http 5001"

echo.
echo ========================================
echo Both services started!
echo.
echo Next steps:
echo 1. Look at the ngrok window
echo 2. Copy the https://xxx.ngrok-free.app URL
echo 3. Update NEXT_PUBLIC_API_URL in Vercel
echo 4. Redeploy on Vercel
echo ========================================
