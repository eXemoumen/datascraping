#!/usr/bin/env python3
"""
Debug script to inspect EspaceAgro HTML structure
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

# Connect to existing Chrome
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")

driver = webdriver.Chrome(options=chrome_options)

# Get current page HTML
print("Getting current page HTML...")
time.sleep(2)

html = driver.page_source

# Save to file
with open("espaceagro_page_debug.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✓ Saved page HTML to: espaceagro_page_debug.html")
print("\nCurrent URL:", driver.current_url)
print("Page title:", driver.title)

# Don't close the driver
driver.quit()
