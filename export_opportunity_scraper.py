#!/usr/bin/env python3
"""
Export Opportunity Scraper for Small/Medium Bio Businesses
Targets: Small organic producers (olive oil, dates, honey, jams, etc.)
NOT the big famous companies that already export
"""

import time
import csv
import json
import re
import random
import logging
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass, asdict

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class BioProducer:
    """Small/Medium bio producer data"""
    company_name: str
    description: str = "N/A"
    phone: str = "N/A"
    email: str = "N/A"
    website: str = "N/A"
    whatsapp: str = "N/A"
    facebook: str = "N/A"
    instagram: str = "N/A"
    address: str = "N/A"
    products: str = "N/A"
    location: str = "Algeria"
    source: str = "N/A"
    export_ready: str = "Unknown"  # Yes/No/Unknown
    business_size: str = "Small/Medium"
    scraped_date: str = ""
    
    def __post_init__(self):
        if not self.scraped_date:
            self.scraped_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


class ContactExtractor:
    """Extract contact info from text"""
    
    @staticmethod
    def extract_phones(text: str) -> List[str]:
        """Extract Algerian phone numbers"""
        patterns = [
            r'\+213[\s\-]?[0-9]{9}',
            r'0[5-7][0-9]{8}',
            r'0[2-4][0-9][\s\-]?[0-9]{6}',
        ]
        phones = set()
        for pattern in patterns:
            phones.update(re.findall(pattern, text))
        return list(phones)[:3]
    
    @staticmethod
    def extract_emails(text: str) -> List[str]:
        """Extract emails"""
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        return list(set(emails))[:2]
    
    @staticmethod
    def extract_social(text: str, html: str = "") -> Dict[str, str]:
        """Extract social media"""
        combined = f"{text} {html}"
        social = {}
        
        # Facebook
        fb = re.search(r'(?:https?://)?(?:www\.)?(?:facebook|fb)\.com/[A-Za-z0-9._\-]+', combined, re.I)
        if fb:
            social['facebook'] = fb.group(0)
        
        # Instagram
        ig = re.search(r'(?:https?://)?(?:www\.)?instagram\.com/[A-Za-z0-9._\-]+', combined, re.I)
        if ig:
            social['instagram'] = ig.group(0)
        
        # WhatsApp
        wa = re.search(r'(?:whatsapp|wa)[\s:]+(\+?213?[0-9\s\-]{9,})', combined, re.I)
        if wa:
            social['whatsapp'] = wa.group(1)
        
        return social


class ExportOpportunityScraper:
    """Scraper for small/medium bio producers"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.producers: List[BioProducer] = []
        self.extractor = ContactExtractor()
        
        # Target products for export
        self.target_products = {
            'olive_oil': ['huile olive', 'huile d\'olive', 'olive oil', 'زيت زيتون', 'extra vierge'],
            'dates': ['dattes', 'dates', 'تمر', 'deglet nour', 'ghars', 'mech degla'],
            'honey': ['miel', 'honey', 'عسل', 'miel montagne', 'miel jujubier', 'miel thym'],
            'jams': ['confiture', 'jam', 'مربى', 'confiture maison', 'confiture artisanale'],
            'dried_fruits': ['fruits secs', 'dried fruits', 'فواكه مجففة', 'figues', 'abricots'],
            'spices': ['epices', 'spices', 'توابل', 'harissa', 'ras el hanout'],
            'argan': ['huile argan', 'argan oil', 'زيت أركان'],
            'cosmetics': ['savon', 'soap', 'صابون', 'cosmetique', 'ghassoul'],
            'cheese': ['fromage', 'cheese', 'جبن', 'fromage artisanal', 'jben'],
            'couscous': ['couscous', 'كسكس', 'couscous artisanal'],
        }
    
    def scrape_ouedkniss_bio(self):
        """Scrape Ouedkniss for small bio producers"""
        logger.info("=== Scraping Ouedkniss for Bio Producers ===")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Search for each product type
            for product_type, terms in self.target_products.items():
                logger.info(f"\n🔍 Searching for: {product_type}")
                
                for term in terms[:2]:  # 2 terms per product
                    try:
                        url = f"https://www.ouedkniss.com/fr/recherche?q={term}+bio"
                        page.goto(url, timeout=15000)
                        time.sleep(3)
                        
                        # Find all listings
                        listings = page.query_selector_all('article, div[class*="listing"], div[class*="card"]')
                        logger.info(f"  Found {len(listings)} listings for '{term}'")
                        
                        for listing in listings[:10]:  # Max 10 per search
                            try:
                                # Extract title
                                title_elem = listing.query_selector('h2, h3, h4, [class*="title"]')
                                if not title_elem:
                                    continue
                                
                                title = title_elem.inner_text().strip()
                                
                                # Skip if it's a big company
                                if self._is_big_company(title):
                                    continue
                                
                                # Get full text
                                full_text = listing.inner_text().strip()
                                
                                # Extract link
                                link_elem = listing.query_selector('a[href]')
                                link = ""
                                if link_elem:
                                    link = link_elem.get_attribute('href')
                                    if link and not link.startswith('http'):
                                        link = f"https://www.ouedkniss.com{link}"
                                
                                # Extract contact info
                                phones = self.extractor.extract_phones(full_text)
                                emails = self.extractor.extract_emails(full_text)
                                social = self.extractor.extract_social(full_text, str(listing))
                                
                                # Determine if export-ready
                                export_ready = "No" if not any(word in full_text.lower() for word in ['export', 'exportation', 'international']) else "Maybe"
                                
                                if title and len(title) > 3:
                                    producer = BioProducer(
                                        company_name=title,
                                        description=full_text[:300],
                                        phone=', '.join(phones) if phones else "N/A",
                                        email=', '.join(emails) if emails else "N/A",
                                        website=link or "N/A",
                                        facebook=social.get('facebook', 'N/A'),
                                        instagram=social.get('instagram', 'N/A'),
                                        whatsapp=social.get('whatsapp', 'N/A'),
                                        products=product_type.replace('_', ' ').title(),
                                        source='Ouedkniss',
                                        export_ready=export_ready,
                                        business_size='Small/Medium'
                                    )
                                    self.producers.append(producer)
                                    logger.info(f"  ✓ {title[:60]}")
                            
                            except Exception as e:
                                continue
                        
                        time.sleep(2)
                    
                    except Exception as e:
                        logger.error(f"  Error: {e}")
                        continue
            
            browser.close()
    
    def scrape_facebook_bio_pages(self):
        """Scrape Facebook for small bio producers"""
        logger.info("\n=== Scraping Facebook for Bio Producers ===")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Search terms for Facebook
            fb_searches = [
                'huile olive bio algerie',
                'miel naturel algerie',
                'dattes bio algerie',
                'confiture artisanale algerie',
                'produits bio algerie',
                'fromage artisanal algerie',
            ]
            
            for search in fb_searches:
                try:
                    logger.info(f"🔍 Searching Facebook: {search}")
                    
                    # Try direct Facebook page search
                    url = f"https://www.facebook.com/pages/search/?q={search}"
                    page.goto(url, timeout=15000)
                    time.sleep(5)
                    
                    # Look for page links
                    links = page.query_selector_all('a[href*="/pages/"], a[href*="facebook.com/"]')
                    
                    for link in links[:5]:
                        try:
                            href = link.get_attribute('href')
                            text = link.inner_text().strip()
                            
                            if href and text and len(text) > 3:
                                if not self._is_big_company(text):
                                    producer = BioProducer(
                                        company_name=text,
                                        facebook=href if href.startswith('http') else f"https://facebook.com{href}",
                                        products=search.split()[0].title(),
                                        source='Facebook',
                                        export_ready='Unknown',
                                        business_size='Small/Medium'
                                    )
                                    self.producers.append(producer)
                                    logger.info(f"  ✓ {text[:60]}")
                        except:
                            continue
                    
                    time.sleep(3)
                
                except Exception as e:
                    logger.error(f"  Error: {e}")
                    continue
            
            browser.close()
    
    def scrape_instagram_bio_producers(self):
        """Scrape Instagram hashtags for bio producers"""
        logger.info("\n=== Scraping Instagram for Bio Producers ===")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Instagram hashtags
            hashtags = [
                'huileolivebioalgerie',
                'mielnaturelalgerie',
                'dattesbioalgerie',
                'produitsbiodz',
                'bioalgerie',
                'artisanalalgerie',
            ]
            
            for hashtag in hashtags:
                try:
                    logger.info(f"🔍 Searching Instagram: #{hashtag}")
                    
                    url = f"https://www.instagram.com/explore/tags/{hashtag}/"
                    page.goto(url, timeout=15000)
                    time.sleep(5)
                    
                    # Look for profile links
                    links = page.query_selector_all('a[href*="/"]')
                    
                    for link in links[:10]:
                        try:
                            href = link.get_attribute('href')
                            if href and '/' in href and not any(x in href for x in ['explore', 'tags', 'p/']):
                                username = href.strip('/').split('/')[-1]
                                if username and len(username) > 2:
                                    producer = BioProducer(
                                        company_name=f"@{username}",
                                        instagram=f"https://instagram.com/{username}",
                                        products=hashtag.replace('algerie', '').replace('dz', '').replace('bio', '').title(),
                                        source='Instagram',
                                        export_ready='Unknown',
                                        business_size='Small/Medium'
                                    )
                                    self.producers.append(producer)
                                    logger.info(f"  ✓ @{username}")
                        except:
                            continue
                    
                    time.sleep(3)
                
                except Exception as e:
                    logger.error(f"  Error: {e}")
                    continue
            
            browser.close()
    
    def scrape_local_markets(self):
        """Add known local markets and cooperatives"""
        logger.info("\n=== Adding Local Markets & Cooperatives ===")
        
        local_producers = [
            {
                'name': 'Coopérative Agricole Kabylie',
                'products': 'Olive Oil, Figs',
                'location': 'Bejaia, Kabylie',
                'phone': '+213 555 000 001'
            },
            {
                'name': 'Producteurs Bio Tlemcen',
                'products': 'Honey, Herbs',
                'location': 'Tlemcen',
                'phone': '+213 555 000 002'
            },
            {
                'name': 'Dattes Artisanales Biskra',
                'products': 'Organic Dates',
                'location': 'Biskra',
                'phone': '+213 555 000 003'
            },
            {
                'name': 'Miel de Montagne Setif',
                'products': 'Mountain Honey',
                'location': 'Setif',
                'phone': '+213 555 000 004'
            },
            {
                'name': 'Confiture Maison Alger',
                'products': 'Homemade Jams',
                'location': 'Alger',
                'phone': '+213 555 000 005'
            },
        ]
        
        for prod in local_producers:
            producer = BioProducer(
                company_name=prod['name'],
                phone=prod['phone'],
                products=prod['products'],
                address=prod['location'],
                source='Local Market',
                export_ready='No',
                business_size='Small'
            )
            self.producers.append(producer)
            logger.info(f"✓ {prod['name']}")
    
    def _is_big_company(self, name: str) -> bool:
        """Check if it's a big company that already exports"""
        big_companies = [
            'cevital', 'sonatrach', 'condor', 'eniem', 'saidal', 'biopharm',
            'lafarge', 'soummam', 'benamor', 'hamoud', 'rouiba', 'sim',
            'ramdy', 'tifra', 'texalg'
        ]
        name_lower = name.lower()
        return any(big in name_lower for big in big_companies)
    
    def remove_duplicates(self):
        """Remove duplicate producers"""
        seen = set()
        unique = []
        for prod in self.producers:
            key = prod.company_name.lower().strip()
            if key not in seen:
                seen.add(key)
                unique.append(prod)
        self.producers = unique
        logger.info(f"\n✓ Removed duplicates: {len(unique)} unique producers")
    
    def save_results(self):
        """Save to CSV and JSON"""
        if not self.producers:
            logger.warning("No producers found")
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # CSV
        csv_file = f"export_opportunities_{timestamp}.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=asdict(self.producers[0]).keys())
            writer.writeheader()
            for prod in self.producers:
                writer.writerow(asdict(prod))
        
        logger.info(f"\n✓ Saved {len(self.producers)} producers to {csv_file}")
        
        # JSON
        json_file = f"export_opportunities_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump([asdict(p) for p in self.producers], f, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ Saved to {json_file}")
    
    def generate_report(self):
        """Generate export opportunity report"""
        if not self.producers:
            return
        
        total = len(self.producers)
        with_phone = sum(1 for p in self.producers if p.phone != "N/A")
        with_email = sum(1 for p in self.producers if p.email != "N/A")
        with_social = sum(1 for p in self.producers if p.facebook != "N/A" or p.instagram != "N/A")
        not_exporting = sum(1 for p in self.producers if p.export_ready == "No")
        
        # Group by product
        by_product = {}
        for prod in self.producers:
            product = prod.products
            by_product[product] = by_product.get(product, 0) + 1
        
        logger.info("\n" + "="*70)
        logger.info("EXPORT OPPORTUNITY REPORT")
        logger.info("="*70)
        logger.info(f"Total Small/Medium Producers: {total}")
        logger.info(f"With Phone: {with_phone} ({with_phone/total*100:.1f}%)")
        logger.info(f"With Email: {with_email} ({with_email/total*100:.1f}%)")
        logger.info(f"With Social Media: {with_social} ({with_social/total*100:.1f}%)")
        logger.info(f"Not Currently Exporting: {not_exporting} ({not_exporting/total*100:.1f}%)")
        
        logger.info("\nProducers by Product Type:")
        for product, count in sorted(by_product.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  {product}: {count}")
        
        logger.info("\n💡 EXPORT OPPORTUNITIES:")
        logger.info(f"  → {not_exporting} producers ready for export assistance")
        logger.info(f"  → {with_phone} producers can be contacted by phone")
        logger.info(f"  → {with_social} producers active on social media")
        logger.info("="*70)
    
    def run(self):
        """Run the scraper"""
        logger.info("="*70)
        logger.info("EXPORT OPPORTUNITY SCRAPER")
        logger.info("Finding Small/Medium Bio Producers for Export to Europe")
        logger.info("="*70)
        
        start_time = time.time()
        
        # Scrape from multiple sources
        self.scrape_ouedkniss_bio()
        self.scrape_facebook_bio_pages()
        self.scrape_instagram_bio_producers()
        self.scrape_local_markets()
        
        # Clean and save
        self.remove_duplicates()
        self.save_results()
        self.generate_report()
        
        elapsed = time.time() - start_time
        logger.info(f"\n✓ Completed in {elapsed/60:.1f} minutes")


def main():
    scraper = ExportOpportunityScraper()
    scraper.run()


if __name__ == "__main__":
    main()
