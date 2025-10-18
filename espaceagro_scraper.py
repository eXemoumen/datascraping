#!/usr/bin/env python3
"""
EspaceAgro Algeria Scraper
Scrapes enterprise announcements from espaceagro.com using your logged-in Chrome session
Extracts: Company names, descriptions, products, locations (without paid contact info)
"""

import time
import csv
import json
import re
import random
import logging
import sqlite3
from datetime import datetime
from typing import List, Dict
from dataclasses import dataclass, asdict
from urllib.parse import quote_plus, urljoin

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class EspaceAgroListing:
    """Enterprise listing from EspaceAgro"""
    company_name: str
    announcement_title: str = "N/A"
    description: str = "N/A"
    products: str = "N/A"
    location: str = "Algeria"
    announcement_type: str = "N/A"  # Vente/Achat/Offre/Demande
    announcement_date: str = "N/A"
    announcement_url: str = "N/A"
    member_id: str = "N/A"
    scraped_date: str = ""
    notes: str = "Contact info requires payment on espaceagro.com"
    
    def __post_init__(self):
        if not self.scraped_date:
            self.scraped_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


class EspaceAgroScraper:
    """Scraper for EspaceAgro Algeria announcements using existing Chrome session"""
    
    def __init__(self, chrome_debugger_port: int = 9222, db_path: str = "espaceagro.db"):
        """
        Initialize scraper to connect to your existing Chrome session
        
        Args:
            chrome_debugger_port: Port for Chrome remote debugging (default: 9222)
            db_path: Path to SQLite database
        """
        self.listings: List[EspaceAgroListing] = []
        self.base_url = "https://www.espaceagro.com"
        self.chrome_debugger_port = chrome_debugger_port
        self.driver = None
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS announcements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id TEXT UNIQUE NOT NULL,
                company_name TEXT,
                announcement_title TEXT,
                description TEXT,
                products TEXT,
                location TEXT,
                announcement_type TEXT,
                announcement_date TEXT,
                announcement_url TEXT,
                scraped_date TEXT,
                notes TEXT,
                checked INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def _announcement_exists(self, member_id: str) -> bool:
        """Check if announcement already exists in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM announcements WHERE member_id = ?', (member_id,))
        exists = cursor.fetchone()[0] > 0
        conn.close()
        return exists
    
    def _save_to_database(self, listing: EspaceAgroListing):
        """Save listing to database if it doesn't exist"""
        if self._announcement_exists(listing.member_id):
            logger.debug(f"  ⏭️  Skipping duplicate: {listing.member_id}")
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO announcements 
            (member_id, company_name, announcement_title, description, products, 
             location, announcement_type, announcement_date, announcement_url, 
             scraped_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            listing.member_id, listing.company_name, listing.announcement_title,
            listing.description, listing.products, listing.location,
            listing.announcement_type, listing.announcement_date,
            listing.announcement_url, listing.scraped_date, listing.notes
        ))
        conn.commit()
        conn.close()
        return True
    
    def connect_to_chrome(self):
        """Connect to existing Chrome session"""
        logger.info("🔗 Connecting to your Chrome browser...")
        
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", f"localhost:{self.chrome_debugger_port}")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("✓ Connected to Chrome successfully!")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to Chrome: {e}")
            logger.info("\n📋 SETUP INSTRUCTIONS:")
            logger.info("1. Close ALL Chrome windows")
            logger.info("2. Open Chrome with remote debugging:")
            logger.info('   Run this command in a new terminal:')
            logger.info(f'   "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port={self.chrome_debugger_port} --user-data-dir="C:\\selenium\\ChromeProfile"')
            logger.info("3. Log in to espaceagro.com in that Chrome window")
            logger.info("4. Run this script again")
            return False
    
    def close(self):
        """Close the driver (but keep Chrome open)"""
        if self.driver:
            self.driver.quit()
        
    def scrape_algeria_announcements(self, max_pages: int = 999):
        """Scrape announcements from Algeria using logged-in Chrome session"""
        logger.info("=== Scraping EspaceAgro Algeria Announcements ===")
        
        if not self.driver:
            logger.error("❌ Not connected to Chrome. Call connect_to_chrome() first.")
            return
        
        # Base URL for Algeria announcements (selling)
        base_search_url = "https://www.espaceagro.com/membres/esindex.asp"
        
        for page_num in range(1, max_pages + 1):
            try:
                logger.info(f"\n📄 Scraping page {page_num}...")
                
                # Build URL with parameters
                # num parameter is the offset: (page_num - 1) * 40
                num_offset = (page_num - 1) * 40
                url = f"{base_search_url}?page={page_num}&TRI=&laction3=3&pays=Algerie&num={num_offset}&dm=&exp=&_LETYPEE=&activite=&sdr="
                
                # Navigate to page
                logger.info(f"Navigating to: {url}")
                try:
                    self.driver.set_page_load_timeout(30)  # 30 second timeout
                    self.driver.get(url)
                    logger.info(f"✓ Page loaded, current URL: {self.driver.current_url}")
                except Exception as e:
                    logger.error(f"⚠️  Page load timeout or error: {e}")
                    logger.info("Retrying page...")
                    time.sleep(5)
                    try:
                        self.driver.get(url)
                    except:
                        logger.error(f"❌ Failed to load page {page_num}, skipping...")
                        continue
                
                # Wait for page to load
                time.sleep(3)
                
                # Get page source and parse
                logger.info(f"📄 Parsing page HTML...")
                page_source = self.driver.page_source
                
                # Check if page loaded properly
                if len(page_source) < 1000:
                    logger.warning(f"⚠️  Page seems too small ({len(page_source)} bytes), might not have loaded properly")
                    logger.info("Waiting 5 more seconds...")
                    time.sleep(5)
                    page_source = self.driver.page_source
                
                soup = BeautifulSoup(page_source, 'html.parser')
                
                # Find announcement listings
                new_announcements, total_found = self._extract_announcements(soup, page_num)
                
                if total_found == 0:
                    logger.warning(f"❌ No announcements found on page {page_num}")
                    if page_num > 1:
                        logger.info("🏁 Reached end of results - no more pages!")
                        break
                    else:
                        logger.error("❌ No announcements found on first page! Check if you're logged in.")
                        break
                
                logger.info(f"✓ Found {total_found} announcements on page {page_num} ({new_announcements} new)")
                logger.info(f"📊 Progress: {len(self.listings)} total announcements scraped so far")
                
                # Random delay between pages (be respectful)
                if page_num < max_pages:
                    delay = random.uniform(3, 6)
                    logger.info(f"⏳ Waiting {delay:.1f}s before next page...")
                    time.sleep(delay)
                    
            except KeyboardInterrupt:
                logger.info(f"\n⚠️  Scraping interrupted by user at page {page_num}")
                logger.info(f"✓ Saved {len(self.listings)} announcements so far")
                break
            except Exception as e:
                logger.error(f"❌ Error on page {page_num}: {e}")
                logger.info("Waiting 10 seconds before retrying...")
                time.sleep(10)
                # Try to continue to next page instead of retrying same page
                logger.info("Skipping to next page...")
                continue
        
        logger.info(f"\n✓ Total announcements scraped: {len(self.listings)}")
    
    def _extract_announcements(self, soup: BeautifulSoup, page_num: int) -> tuple:
        """Extract announcement data from page. Returns (new_count, total_count)"""
        new_count = 0
        total_count = 0
        
        # EspaceAgro uses specific div structure for announcements
        listing_containers = soup.find_all('div', class_=re.compile(r'contanier-fluid M40 PB15'))
        
        logger.info(f"🔍 Found {len(listing_containers)} announcement containers on page {page_num}")
        
        # If no containers found, try alternative selectors
        if len(listing_containers) == 0:
            logger.warning("⚠️  No containers with 'contanier-fluid M40 PB15' found, trying alternatives...")
            listing_containers = soup.find_all('div', class_=re.compile(r'M40'))
            logger.info(f"🔍 Found {len(listing_containers)} containers with 'M40' class")
            
            # If still nothing, save HTML for debugging
            if len(listing_containers) == 0:
                logger.error(f"❌ No containers found at all on page {page_num}!")
                with open(f'debug_page_{page_num}.html', 'w', encoding='utf-8') as f:
                    f.write(str(soup))
                logger.info(f"💾 Saved page HTML to debug_page_{page_num}.html")
        
        for container in listing_containers:
            try:
                listing = self._parse_listing(container)
                if listing and listing.announcement_title != "N/A" and listing.member_id != "N/A":
                    total_count += 1
                    # Save to database (only if new)
                    if self._save_to_database(listing):
                        self.listings.append(listing)
                        new_count += 1
                        logger.info(f"  ✓ NEW: {listing.announcement_title[:60]}")
                    else:
                        logger.info(f"  ⏭️  Exists: {listing.announcement_title[:60]}")
            except Exception as e:
                logger.debug(f"  Skipped listing: {e}")
                continue
        
        return new_count, total_count
    
    def _parse_listing(self, container) -> EspaceAgroListing:
        """Parse individual listing"""
        text = container.get_text(separator=' ', strip=True)
        
        # Extract announcement ID and title
        announcement_id = "N/A"
        title = "N/A"
        title_link = container.find('a', href=re.compile(r'esvoir\.asp\?id='))
        if title_link:
            title = title_link.get_text(strip=True)
            # Extract ID from URL
            id_match = re.search(r'id=(\d+)', title_link.get('href', ''))
            if id_match:
                announcement_id = id_match.group(1)
        
        # Extract announcement URL
        url = "N/A"
        if title_link:
            href = title_link['href']
            if href.startswith('http'):
                url = href
            else:
                # Fix: Add /membres/ prefix to the URL
                if 'esvoir.asp' in href and '/membres/' not in href:
                    href = '/membres/' + href.lstrip('/')
                url = urljoin(self.base_url, href)
        
        # Extract company/business type (fabricant, producteur, etc.)
        company_type = "N/A"
        type_match = re.search(r'(fabricant|producteur|grossiste|distributeur|fournisseur|exportateur|importateur)', text, re.I)
        if type_match:
            company_type = type_match.group(1)
        
        # Extract description (the main text paragraph)
        description = "N/A"
        desc_paragraph = container.find('p')
        if desc_paragraph:
            description = desc_paragraph.get_text(separator=' ', strip=True)[:500]
        
        # Extract products (look for keywords)
        products = self._extract_products(text)
        
        # Extract rubrique (category)
        rubrique = "N/A"
        rubrique_link = container.find('a', href=re.compile(r'esindex\.asp\?dm='))
        if rubrique_link:
            rubrique = rubrique_link.get_text(strip=True)
        
        # Extract location
        location = "Algeria"
        location_match = re.search(r'Annonceur de\s+&nbsp;<a[^>]*>([^<]+)</a>', str(container), re.I)
        if location_match:
            location = location_match.group(1).strip()
        else:
            # Try other location patterns
            location_match = re.search(r'(Alger|Oran|Constantine|Bejaia|Tizi Ouzou|Setif|Biskra|Tlemcen|Batna|Blida|Annaba)', text, re.I)
            if location_match:
                location = location_match.group(1)
        
        # Extract announcement type from label
        announcement_type = "N/A"
        label = container.find('span', class_='label')
        if label:
            announcement_type = label.get_text(strip=True)
        
        # Extract date
        date = "N/A"
        if "Aujourd'hui" in text or "aujourd'hui" in text:
            date = "Aujourd'hui"
        else:
            date_match = re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', text)
            if date_match:
                date = date_match.group(0)
        
        return EspaceAgroListing(
            company_name=company_type,
            announcement_title=title,
            description=description,
            products=f"{rubrique}, {products}" if products != "N/A" else rubrique,
            location=location,
            announcement_type=announcement_type,
            announcement_date=date,
            announcement_url=url,
            member_id=announcement_id
        )
    
    def _extract_products(self, text: str) -> str:
        """Extract product types from text"""
        products = []
        
        product_keywords = {
            'huile': 'Huile',
            'olive': 'Olive',
            'dattes': 'Dattes',
            'miel': 'Miel',
            'fruits': 'Fruits',
            'legumes': 'Légumes',
            'cereales': 'Céréales',
            'epices': 'Épices',
            'viande': 'Viande',
            'poisson': 'Poisson',
            'lait': 'Produits laitiers',
            'fromage': 'Fromage',
            'bio': 'Bio',
            'agriculture': 'Agriculture',
        }
        
        text_lower = text.lower()
        for keyword, product in product_keywords.items():
            if keyword in text_lower and product not in products:
                products.append(product)
        
        return ', '.join(products) if products else "N/A"
    
    def save_results(self):
        """Save results to CSV and JSON"""
        if not self.listings:
            logger.warning("No listings to save")
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save to CSV
        csv_file = f"espaceagro_algeria_{timestamp}.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=asdict(self.listings[0]).keys())
            writer.writeheader()
            for listing in self.listings:
                writer.writerow(asdict(listing))
        
        logger.info(f"\n✓ Saved {len(self.listings)} listings to {csv_file}")
        
        # Save to JSON
        json_file = f"espaceagro_algeria_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump([asdict(l) for l in self.listings], f, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ Saved to {json_file}")
    
    def generate_report(self):
        """Generate summary report"""
        if not self.listings:
            return
        
        total = len(self.listings)
        
        # Group by products
        by_product = {}
        for listing in self.listings:
            products = listing.products.split(', ')
            for product in products:
                if product != "N/A":
                    by_product[product] = by_product.get(product, 0) + 1
        
        # Group by location
        by_location = {}
        for listing in self.listings:
            loc = listing.location
            by_location[loc] = by_location.get(loc, 0) + 1
        
        logger.info("\n" + "="*70)
        logger.info("ESPACEAGRO ALGERIA SCRAPING REPORT")
        logger.info("="*70)
        logger.info(f"Total Announcements: {total}")
        
        logger.info("\nTop Products:")
        for product, count in sorted(by_product.items(), key=lambda x: x[1], reverse=True)[:10]:
            logger.info(f"  {product}: {count}")
        
        logger.info("\nBy Location:")
        for location, count in sorted(by_location.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  {location}: {count}")
        
        logger.info("\n💡 NEXT STEPS:")
        logger.info("  1. Review the CSV file to identify interesting enterprises")
        logger.info("  2. Note the announcement URLs for enterprises you want to contact")
        logger.info("  3. Pay on espaceagro.com to unlock contact details for selected enterprises")
        logger.info("="*70)


def main():
    """Main execution"""
    scraper = EspaceAgroScraper()
    
    # Connect to your existing Chrome session
    if not scraper.connect_to_chrome():
        logger.error("❌ Could not connect to Chrome. Please follow the setup instructions above.")
        return
    
    try:
        # Scrape Algeria announcements (will continue until no more pages)
        scraper.scrape_algeria_announcements(max_pages=999)
        
        # Save results
        scraper.save_results()
        
        # Generate report
        scraper.generate_report()
    
    finally:
        # Close connection (Chrome window stays open)
        scraper.close()


if __name__ == "__main__":
    main()
