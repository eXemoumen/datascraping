@echo off
echo Starting Chrome with remote debugging...
echo.
echo INSTRUCTIONS:
echo 1. Chrome will open in a new window
echo 2. Log in to espaceagro.com
echo 3. Keep this Chrome window open
echo 4. Run: python espaceagro_scraper.py
echo.
pause

"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\selenium\ChromeProfile"
