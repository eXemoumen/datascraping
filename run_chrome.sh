#!/bin/bash
echo "🚀 Starting Chrome in Debug Mode..."
"C:/Program Files/Google/Chrome/Application/chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:/selenium/ChromeProfile"
Start-Process "C:\Program Files\Google\Chrome\Application\chrome.exe" -ArgumentList "--remote-debugging-port=9222","--user-data-dir=C:\selenium\ChromeProfile"