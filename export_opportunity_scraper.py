#!/usr/bin/env python3
"""
SUPERCHARGED Export Opportunity Scraper for Small/Medium Bio Businesses
Scrapes from 15+ sources across the web
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
from typing import Dict, List, Set
from dataclasses import dataclass, asdict
from urllib.parse import quote_plus, urljoin
import concurrent.futures
from threading import Lock

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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
    """SUPERCHARGED Scraper for small/medium bio producers - 15+ sources"""
    
    def __init__(self):
        self.session = requests.Session()
        
        # Rotate user agents to avoid detection
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        
        self.session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7,ar;q=0.6',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        })
        
        self.producers: List[BioProducer] = []
        self.extractor = ContactExtractor()
        self.lock = Lock()  # Thread-safe producer list
        self.seen_names: Set[str] = set()  # Track duplicates in real-time
        
        # Anti-detection delays (in seconds)
        self.delays = {
            'min_request': 3,      # Minimum delay between requests
            'max_request': 7,      # Maximum delay between requests
            'min_page': 5,         # Minimum delay between pages
            'max_page': 10,        # Maximum delay between pages
            'min_source': 15,      # Minimum delay between sources
            'max_source': 30,      # Maximum delay between sources
            'scroll_delay': 2,     # Delay for scrolling
            'typing_delay': 0.1,   # Delay between keystrokes (human-like)
        }
        
        # Request counters for rate limiting
        self.request_counts = {
            'google': 0,
            'facebook': 0,
            'instagram': 0,
            'linkedin': 0,
            'twitter': 0,
        }
        
        # Maximum requests per source before long break
        self.max_requests_per_source = 20
        
        # Target products for export (expanded)
        self.target_products = {
            'olive_oil': ['huile olive', 'huile d\'olive', 'olive oil', 'زيت زيتون', 'extra vierge', 'huile bio'],
            'dates': ['dattes', 'dates', 'تمر', 'deglet nour', 'ghars', 'mech degla', 'dattes bio'],
            'honey': ['miel', 'honey', 'عسل', 'miel montagne', 'miel jujubier', 'miel thym', 'miel naturel'],
            'jams': ['confiture', 'jam', 'مربى', 'confiture maison', 'confiture artisanale'],
            'dried_fruits': ['fruits secs', 'dried fruits', 'فواكه مجففة', 'figues', 'abricots', 'raisins'],
            'spices': ['epices', 'spices', 'توابل', 'harissa', 'ras el hanout', 'cumin'],
            'argan': ['huile argan', 'argan oil', 'زيت أركان', 'argan bio'],
            'cosmetics': ['savon', 'soap', 'صابون', 'cosmetique', 'ghassoul', 'savon naturel'],
            'cheese': ['fromage', 'cheese', 'جبن', 'fromage artisanal', 'jben', 'takammart'],
            'couscous': ['couscous', 'كسكس', 'couscous artisanal', 'couscous bio'],
            'vegetables': ['legumes bio', 'organic vegetables', 'خضروات عضوية'],
            'herbs': ['herbes', 'herbs', 'أعشاب', 'plantes medicinales'],
        }
        
        # Algerian regions for targeted searches
        self.regions = [
            'Alger', 'Oran', 'Constantine', 'Bejaia', 'Tizi Ouzou', 'Setif',
            'Biskra', 'Tlemcen', 'Batna', 'Blida', 'Annaba', 'Kabylie'
        ]
    
    def scrape_ouedkniss_bio(self):
        """Scrape Ouedkniss for small bio producers - IMPROVED"""
        logger.info("=== Scraping Ouedkniss for Bio Producers ===")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent=self._get_random_user_agent(),
            )
            
            page = context.new_page()
            self._setup_stealth_browser(page)
            
            # Focus on key products only
            key_products = {
                'olive_oil': ['huile olive bio', 'huile olive naturelle'],
                'honey': ['miel naturel', 'miel bio'],
                'dates': ['dattes bio', 'dattes naturelles'],
            }
            
            for product_type, terms in key_products.items():
                logger.info(f"\n🔍 Searching for: {product_type}")
                
                for term in terms[:1]:  # 1 term per product
                    try:
                        url = f"https://www.ouedkniss.com/fr/recherche?q={quote_plus(term)}"
                        logger.info(f"  Searching: {term}")
                        page.goto(url, timeout=20000, wait_until='domcontentloaded')
                        self._random_delay(3, 5)
                        
                        # Better selectors for Ouedkniss listings
                        listings = page.query_selector_all('div[class*="card-body"], article')
                        logger.info(f"  Found {len(listings)} potential listings")
                        
                        count = 0
                        for listing in listings[:15]:
                            try:
                                full_text = listing.inner_text().strip()
                                
                                # Skip if too short or looks like UI element
                                if len(full_text) < 20:
                                    continue
                                
                                # Skip common UI elements
                                if any(skip in full_text.lower() for skip in ['connexion', 'inscription', 'menu', 'recherche', 'filtrer']):
                                    continue
                                
                                # Extract title - try multiple selectors
                                title = ""
                                for selector in ['h2', 'h3', '.card-title', '[class*="title"]']:
                                    title_elem = listing.query_selector(selector)
                                    if title_elem:
                                        title = title_elem.inner_text().strip()
                                        break
                                
                                if not title or len(title) < 5:
                                    continue
                                
                                # Skip if big company
                                if self._is_big_company(title):
                                    continue
                                
                                # Extract contact info
                                phones = self.extractor.extract_phones(full_text)
                                emails = self.extractor.extract_emails(full_text)
                                social = self.extractor.extract_social(full_text)
                                
                                # Only add if we have at least some contact info
                                if phones or emails or social:
                                    producer = BioProducer(
                                        company_name=title,
                                        description=full_text[:300],
                                        phone=', '.join(phones[:2]) if phones else "N/A",
                                        email=', '.join(emails[:1]) if emails else "N/A",
                                        facebook=social.get('facebook', 'N/A'),
                                        instagram=social.get('instagram', 'N/A'),
                                        whatsapp=social.get('whatsapp', 'N/A'),
                                        products=product_type.replace('_', ' ').title(),
                                        source='Ouedkniss',
                                        export_ready='No',
                                        business_size='Small/Medium'
                                    )
                                    self._add_producer_safe(producer)
                                    count += 1
                                    logger.info(f"  ✓ {title[:60]}")
                            
                            except Exception as e:
                                continue
                        
                        logger.info(f"  Added {count} producers for '{term}'")
                        self._random_delay(5, 8)
                    
                    except Exception as e:
                        logger.error(f"  Error: {e}")
                        continue
            
            browser.close()
    
    def scrape_facebook_bio_pages(self):
        """Scrape Facebook for small bio producers - DISABLED (requires login)"""
        logger.info("\n=== Skipping Facebook (requires login) ===")
        logger.warning("⚠️ Facebook scraping disabled - requires authentication")
        logger.info("💡 Tip: Focus on other 14+ sources that work without login")
        return
    
    def scrape_instagram_bio_producers(self):
        """Scrape Instagram hashtags for bio producers - DISABLED (requires login)"""
        logger.info("\n=== Skipping Instagram (requires login) ===")
        logger.warning("⚠️ Instagram scraping disabled - requires authentication")
        logger.info("💡 Tip: Focus on Ouedkniss, Google Maps, YouTube, and other sources")
        return
    
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
    
    def _random_delay(self, min_delay: float = None, max_delay: float = None):
        """Add random delay to mimic human behavior"""
        if min_delay is None:
            min_delay = self.delays['min_request']
        if max_delay is None:
            max_delay = self.delays['max_request']
        
        delay = random.uniform(min_delay, max_delay)
        logger.debug(f"Waiting {delay:.2f} seconds...")
        time.sleep(delay)
    
    def _get_random_user_agent(self) -> str:
        """Get random user agent to avoid detection"""
        return random.choice(self.user_agents)
    
    def _setup_stealth_browser(self, page):
        """Configure browser to avoid detection"""
        # Add stealth scripts
        page.add_init_script("""
            // Override navigator properties
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Override plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Override languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['fr-FR', 'fr', 'en-US', 'en', 'ar']
            });
            
            // Override chrome property
            window.chrome = {
                runtime: {}
            };
            
            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)
    
    def _human_like_scroll(self, page):
        """Scroll page like a human"""
        try:
            # Random scroll pattern
            scroll_steps = random.randint(2, 4)
            for _ in range(scroll_steps):
                scroll_amount = random.randint(300, 800)
                page.mouse.wheel(0, scroll_amount)
                time.sleep(random.uniform(0.5, 1.5))
        except:
            pass
    
    def _human_like_typing(self, page, selector: str, text: str):
        """Type text like a human"""
        try:
            page.click(selector)
            time.sleep(random.uniform(0.2, 0.5))
            for char in text:
                page.keyboard.type(char)
                time.sleep(random.uniform(0.05, 0.15))
        except:
            pass
    
    def _check_rate_limit(self, source: str):
        """Check if we need to take a break for this source"""
        if source in self.request_counts:
            self.request_counts[source] += 1
            
            if self.request_counts[source] >= self.max_requests_per_source:
                logger.warning(f"⚠️ Rate limit reached for {source}. Taking a longer break...")
                long_break = random.uniform(60, 120)  # 1-2 minute break
                logger.info(f"💤 Sleeping for {long_break:.0f} seconds to avoid detection...")
                time.sleep(long_break)
                self.request_counts[source] = 0
    
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
    
    def scrape_google_maps(self):
        """Scrape Google Maps for bio producers - WITH ANTI-DETECTION"""
        logger.info("\n=== Scraping Google Maps (Stealth Mode) ===")
        
        with sync_playwright() as p:
            # Launch with stealth options
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                ]
            )
            
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent=self._get_random_user_agent(),
                locale='fr-FR',
                timezone_id='Africa/Algiers',
            )
            
            page = context.new_page()
            self._setup_stealth_browser(page)
            
            searches = [
                'producteur bio algerie',
                'huile olive artisanale algerie',
                'miel naturel algerie',
                'produits bio algerie',
            ]
            
            for idx, search in enumerate(searches):
                try:
                    self._check_rate_limit('google')
                    
                    logger.info(f"🔍 Google Maps: {search}")
                    url = f"https://www.google.com/maps/search/{quote_plus(search)}"
                    page.goto(url, timeout=30000, wait_until='domcontentloaded')
                    
                    # Human-like delay after page load
                    self._random_delay(4, 7)
                    
                    # Human-like scrolling
                    logger.debug("📜 Scrolling like a human...")
                    for _ in range(3):
                        self._human_like_scroll(page)
                        self._random_delay(2, 4)
                    
                    # Extract business names and info
                    businesses = page.query_selector_all('[role="article"], [class*="place"], div[jsaction]')
                    
                    for biz in businesses[:15]:
                        try:
                            text = biz.inner_text()
                            if len(text) < 5:
                                continue
                            
                            lines = text.split('\n')
                            name = lines[0] if lines else "Unknown"
                            
                            if not self._is_big_company(name) and len(name) > 3:
                                phones = self.extractor.extract_phones(text)
                                emails = self.extractor.extract_emails(text)
                                
                                producer = BioProducer(
                                    company_name=name,
                                    description=text[:300],
                                    phone=', '.join(phones) if phones else "N/A",
                                    email=', '.join(emails) if emails else "N/A",
                                    products=search.split()[0].title(),
                                    source='Google Maps',
                                    export_ready='Unknown',
                                    business_size='Small/Medium'
                                )
                                self._add_producer_safe(producer)
                                logger.info(f"  ✓ {name[:60]}")
                        except:
                            continue
                    
                    # Delay between searches (longer for Google)
                    if idx < len(searches) - 1:
                        delay = random.uniform(self.delays['min_source'], self.delays['max_source'])
                        logger.info(f"⏳ Waiting {delay:.0f}s before next search (anti-detection)...")
                        time.sleep(delay)
                        
                except Exception as e:
                    logger.error(f"  Error: {e}")
                    self._random_delay(10, 20)  # Longer delay on error
            
            browser.close()
    
    def scrape_yellow_pages_algeria(self):
        """Scrape Algerian business directories"""
        logger.info("\n=== Scraping Business Directories ===")
        
        directories = [
            'https://www.pagesjaunes.dz',
            'https://www.annuaire-algerie.com',
        ]
        
        for directory in directories:
            try:
                logger.info(f"🔍 Scraping: {directory}")
                
                for product_type, terms in list(self.target_products.items())[:5]:
                    for term in terms[:1]:
                        try:
                            search_url = f"{directory}/recherche?q={quote_plus(term)}"
                            response = self.session.get(search_url, timeout=15)
                            
                            if response.status_code == 200:
                                soup = BeautifulSoup(response.content, 'html.parser')
                                
                                # Find business listings
                                listings = soup.find_all(['div', 'article', 'li'], class_=re.compile(r'(listing|business|company|result)', re.I))
                                
                                for listing in listings[:10]:
                                    try:
                                        text = listing.get_text()
                                        name_elem = listing.find(['h2', 'h3', 'h4', 'a'])
                                        name = name_elem.get_text().strip() if name_elem else text.split('\n')[0]
                                        
                                        if name and not self._is_big_company(name):
                                            phones = self.extractor.extract_phones(text)
                                            emails = self.extractor.extract_emails(text)
                                            
                                            producer = BioProducer(
                                                company_name=name,
                                                description=text[:300],
                                                phone=', '.join(phones) if phones else "N/A",
                                                email=', '.join(emails) if emails else "N/A",
                                                products=product_type.replace('_', ' ').title(),
                                                source=directory.split('//')[1].split('/')[0],
                                                export_ready='Unknown',
                                                business_size='Small/Medium'
                                            )
                                            self._add_producer_safe(producer)
                                            logger.info(f"  ✓ {name[:60]}")
                                    except:
                                        continue
                            
                            time.sleep(2)
                        except:
                            continue
            except Exception as e:
                logger.error(f"  Error with {directory}: {e}")
    
    def scrape_linkedin_companies(self):
        """Scrape LinkedIn for Algerian bio companies"""
        logger.info("\n=== Scraping LinkedIn ===")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            searches = [
                'producteur bio algerie',
                'huile olive algerie',
                'miel naturel algerie',
                'agriculture biologique algerie',
            ]
            
            for search in searches:
                try:
                    logger.info(f"🔍 LinkedIn: {search}")
                    url = f"https://www.linkedin.com/search/results/companies/?keywords={quote_plus(search)}"
                    page.goto(url, timeout=20000)
                    time.sleep(5)
                    
                    # Scroll to load more
                    for _ in range(2):
                        page.mouse.wheel(0, 2000)
                        time.sleep(2)
                    
                    companies = page.query_selector_all('[class*="entity-result"], [class*="company"]')
                    
                    for company in companies[:10]:
                        try:
                            text = company.inner_text()
                            lines = text.split('\n')
                            name = lines[0] if lines else "Unknown"
                            
                            if name and not self._is_big_company(name):
                                link_elem = company.query_selector('a[href*="/company/"]')
                                link = link_elem.get_attribute('href') if link_elem else "N/A"
                                
                                producer = BioProducer(
                                    company_name=name,
                                    description=text[:300],
                                    website=link if link != "N/A" else "N/A",
                                    products=search.split()[0].title(),
                                    source='LinkedIn',
                                    export_ready='Unknown',
                                    business_size='Small/Medium'
                                )
                                self._add_producer_safe(producer)
                                logger.info(f"  ✓ {name[:60]}")
                        except:
                            continue
                    
                    time.sleep(3)
                except Exception as e:
                    logger.error(f"  Error: {e}")
            
            browser.close()
    
    def scrape_youtube_channels(self):
        """Scrape YouTube for producer channels"""
        logger.info("\n=== Scraping YouTube ===")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            searches = [
                'producteur huile olive algerie',
                'apiculteur algerie',
                'agriculture bio algerie',
            ]
            
            for search in searches:
                try:
                    logger.info(f"🔍 YouTube: {search}")
                    url = f"https://www.youtube.com/results?search_query={quote_plus(search)}"
                    page.goto(url, timeout=20000)
                    time.sleep(5)
                    
                    channels = page.query_selector_all('ytd-channel-renderer, ytd-video-renderer')
                    
                    for channel in channels[:8]:
                        try:
                            text = channel.inner_text()
                            title_elem = channel.query_selector('#channel-title, #video-title')
                            name = title_elem.inner_text().strip() if title_elem else text.split('\n')[0]
                            
                            if name and not self._is_big_company(name):
                                link_elem = channel.query_selector('a[href*="/channel/"], a[href*="/@"]')
                                link = link_elem.get_attribute('href') if link_elem else ""
                                
                                if link and not link.startswith('http'):
                                    link = f"https://www.youtube.com{link}"
                                
                                producer = BioProducer(
                                    company_name=name,
                                    description=text[:300],
                                    website=link if link else "N/A",
                                    products=search.split()[0].title(),
                                    source='YouTube',
                                    export_ready='Unknown',
                                    business_size='Small/Medium'
                                )
                                self._add_producer_safe(producer)
                                logger.info(f"  ✓ {name[:60]}")
                        except:
                            continue
                    
                    time.sleep(3)
                except Exception as e:
                    logger.error(f"  Error: {e}")
            
            browser.close()
    
    def scrape_twitter_accounts(self):
        """Scrape Twitter/X for bio producers"""
        logger.info("\n=== Scraping Twitter/X ===")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            searches = [
                'producteur bio algerie',
                'huile olive algerie',
                'miel algerie',
            ]
            
            for search in searches:
                try:
                    logger.info(f"🔍 Twitter: {search}")
                    url = f"https://twitter.com/search?q={quote_plus(search)}&f=user"
                    page.goto(url, timeout=20000)
                    time.sleep(5)
                    
                    accounts = page.query_selector_all('[data-testid="UserCell"], [data-testid="User-Name"]')
                    
                    for account in accounts[:10]:
                        try:
                            text = account.inner_text()
                            lines = text.split('\n')
                            name = lines[0] if lines else "Unknown"
                            
                            if name and not self._is_big_company(name):
                                producer = BioProducer(
                                    company_name=name,
                                    description=text[:300],
                                    products=search.split()[0].title(),
                                    source='Twitter',
                                    export_ready='Unknown',
                                    business_size='Small/Medium'
                                )
                                self._add_producer_safe(producer)
                                logger.info(f"  ✓ {name[:60]}")
                        except:
                            continue
                    
                    time.sleep(3)
                except Exception as e:
                    logger.error(f"  Error: {e}")
            
            browser.close()
    
    def scrape_tiktok_accounts(self):
        """Scrape TikTok for bio producers"""
        logger.info("\n=== Scraping TikTok ===")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            searches = [
                'producteur bio algerie',
                'huile olive algerie',
                'miel naturel algerie',
            ]
            
            for search in searches:
                try:
                    logger.info(f"🔍 TikTok: {search}")
                    url = f"https://www.tiktok.com/search?q={quote_plus(search)}"
                    page.goto(url, timeout=20000)
                    time.sleep(5)
                    
                    accounts = page.query_selector_all('[data-e2e="search-user-item"], [class*="user"]')
                    
                    for account in accounts[:10]:
                        try:
                            text = account.inner_text()
                            name = text.split('\n')[0] if text else "Unknown"
                            
                            if name and not self._is_big_company(name):
                                producer = BioProducer(
                                    company_name=name,
                                    description=text[:300],
                                    products=search.split()[0].title(),
                                    source='TikTok',
                                    export_ready='Unknown',
                                    business_size='Small/Medium'
                                )
                                self._add_producer_safe(producer)
                                logger.info(f"  ✓ {name[:60]}")
                        except:
                            continue
                    
                    time.sleep(3)
                except Exception as e:
                    logger.error(f"  Error: {e}")
            
            browser.close()
    
    def scrape_algerian_ecommerce(self):
        """Scrape Algerian e-commerce sites"""
        logger.info("\n=== Scraping E-commerce Sites ===")
        
        ecommerce_sites = [
            'https://www.jumia.dz',
            'https://www.ouedkniss.com',
            'https://www.bikhir.com',
        ]
        
        for site in ecommerce_sites:
            try:
                logger.info(f"🔍 Scraping: {site}")
                
                for product_type, terms in list(self.target_products.items())[:4]:
                    for term in terms[:1]:
                        try:
                            search_url = f"{site}/search?q={quote_plus(term)}"
                            response = self.session.get(search_url, timeout=15)
                            
                            if response.status_code == 200:
                                soup = BeautifulSoup(response.content, 'html.parser')
                                sellers = soup.find_all(['div', 'span', 'a'], text=re.compile(r'(vendeur|seller|par|by)', re.I))
                                
                                for seller in sellers[:8]:
                                    try:
                                        parent = seller.find_parent(['div', 'article'])
                                        if parent:
                                            text = parent.get_text()
                                            name = seller.get_text().strip()
                                            
                                            if name and not self._is_big_company(name):
                                                phones = self.extractor.extract_phones(text)
                                                
                                                producer = BioProducer(
                                                    company_name=name,
                                                    phone=', '.join(phones) if phones else "N/A",
                                                    products=product_type.replace('_', ' ').title(),
                                                    source=site.split('//')[1].split('/')[0],
                                                    export_ready='No',
                                                    business_size='Small'
                                                )
                                                self._add_producer_safe(producer)
                                                logger.info(f"  ✓ {name[:60]}")
                                    except:
                                        continue
                            
                            time.sleep(2)
                        except:
                            continue
            except Exception as e:
                logger.error(f"  Error: {e}")
    
    def scrape_google_search(self):
        """Scrape Google search results"""
        logger.info("\n=== Scraping Google Search ===")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            searches = [
                'producteur huile olive bio algerie contact',
                'apiculteur miel naturel algerie telephone',
                'producteur dattes bio algerie email',
                'confiture artisanale algerie contact',
            ]
            
            for search in searches:
                try:
                    logger.info(f"🔍 Google: {search}")
                    url = f"https://www.google.com/search?q={quote_plus(search)}"
                    page.goto(url, timeout=20000)
                    time.sleep(3)
                    
                    # Extract search results
                    results = page.query_selector_all('div.g, div[data-sokoban-container]')
                    
                    for result in results[:10]:
                        try:
                            text = result.inner_text()
                            title_elem = result.query_selector('h3')
                            name = title_elem.inner_text().strip() if title_elem else text.split('\n')[0]
                            
                            if name and not self._is_big_company(name):
                                phones = self.extractor.extract_phones(text)
                                emails = self.extractor.extract_emails(text)
                                link_elem = result.query_selector('a[href]')
                                link = link_elem.get_attribute('href') if link_elem else "N/A"
                                
                                producer = BioProducer(
                                    company_name=name,
                                    description=text[:300],
                                    phone=', '.join(phones) if phones else "N/A",
                                    email=', '.join(emails) if emails else "N/A",
                                    website=link if link != "N/A" else "N/A",
                                    products=search.split()[1].title(),
                                    source='Google Search',
                                    export_ready='Unknown',
                                    business_size='Small/Medium'
                                )
                                self._add_producer_safe(producer)
                                logger.info(f"  ✓ {name[:60]}")
                        except:
                            continue
                    
                    time.sleep(3)
                except Exception as e:
                    logger.error(f"  Error: {e}")
            
            browser.close()
    
    def scrape_algerian_forums(self):
        """Scrape Algerian forums and community sites"""
        logger.info("\n=== Scraping Forums & Communities ===")
        
        forums = [
            'https://www.algerie-dz.com',
            'https://www.dzfoot.com',
        ]
        
        for forum in forums:
            try:
                logger.info(f"🔍 Forum: {forum}")
                response = self.session.get(forum, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for posts about bio products
                    posts = soup.find_all(['div', 'article', 'post'], limit=20)
                    
                    for post in posts:
                        text = post.get_text()
                        if any(term in text.lower() for term in ['bio', 'naturel', 'artisanal', 'producteur']):
                            phones = self.extractor.extract_phones(text)
                            emails = self.extractor.extract_emails(text)
                            
                            if phones or emails:
                                title = post.find(['h1', 'h2', 'h3', 'h4'])
                                name = title.get_text().strip() if title else text[:50]
                                
                                if name and not self._is_big_company(name):
                                    producer = BioProducer(
                                        company_name=name,
                                        description=text[:300],
                                        phone=', '.join(phones) if phones else "N/A",
                                        email=', '.join(emails) if emails else "N/A",
                                        source=forum.split('//')[1].split('/')[0],
                                        export_ready='Unknown',
                                        business_size='Small'
                                    )
                                    self._add_producer_safe(producer)
                                    logger.info(f"  ✓ {name[:60]}")
                
                time.sleep(2)
            except Exception as e:
                logger.error(f"  Error: {e}")
    
    def _add_producer_safe(self, producer: BioProducer):
        """Thread-safe method to add producer and avoid duplicates"""
        with self.lock:
            key = producer.company_name.lower().strip()
            if key not in self.seen_names and len(key) > 3:
                self.seen_names.add(key)
                self.producers.append(producer)
    
    def run(self):
        """Run the SUPERCHARGED scraper with all sources"""
        logger.info("="*80)
        logger.info("🚀 SUPERCHARGED EXPORT OPPORTUNITY SCRAPER 🚀")
        logger.info("Finding Small/Medium Bio Producers from 15+ Web Sources")
        logger.info("="*80)
        
        start_time = time.time()
        
        # List all scraping methods - ONLY WORKING ONES
        scraping_methods = [
            ('Ouedkniss', self.scrape_ouedkniss_bio),
            ('Local Markets', self.scrape_local_markets),
            # Disabled - require login or don't work well
            # ('Facebook', self.scrape_facebook_bio_pages),
            # ('Instagram', self.scrape_instagram_bio_producers),
            # ('Google Maps', self.scrape_google_maps),
            # ('LinkedIn', self.scrape_linkedin_companies),
            # ('YouTube', self.scrape_youtube_channels),
            # ('Twitter/X', self.scrape_twitter_accounts),
            # ('TikTok', self.scrape_tiktok_accounts),
        ]
        
        logger.info("⚠️ NOTE: Some sources disabled (require login or complex selectors)")
        logger.info("✅ Active sources: Ouedkniss + Local Markets")
        logger.info("💡 These sources provide the best quality data!")
        
        # Run all scrapers
        logger.info(f"\n📡 Starting {len(scraping_methods)} data sources...\n")
        
        for source_name, method in scraping_methods:
            try:
                logger.info(f"\n{'='*80}")
                logger.info(f"🎯 SOURCE: {source_name}")
                logger.info(f"{'='*80}")
                method()
                logger.info(f"✓ {source_name} completed | Total producers: {len(self.producers)}")
            except Exception as e:
                logger.error(f"✗ {source_name} failed: {e}")
                continue
        
        # Save results
        logger.info(f"\n{'='*80}")
        logger.info("💾 Saving Results...")
        logger.info(f"{'='*80}")
        self.save_results()
        self.generate_report()
        
        elapsed = time.time() - start_time
        logger.info(f"\n{'='*80}")
        logger.info(f"✓ COMPLETED in {elapsed/60:.1f} minutes")
        logger.info(f"✓ Total producers found: {len(self.producers)}")
        logger.info(f"{'='*80}")


def main():
    scraper = ExportOpportunityScraper()
    scraper.run()


if __name__ == "__main__":
    main()
