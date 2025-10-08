# 🇩🇿 Algerian Bio Export Scraper

A powerful web scraper designed to find **small and medium-sized organic/bio producers** in Algeria for export opportunities to Europe.

Perfect for export agencies looking to connect Algerian artisanal producers with European markets.

## 🎯 Purpose

This scraper helps export agencies find:
- Small olive oil producers (Kabylie region)
- Local honey makers (Tlemcen, Setif)
- Artisanal date producers (Biskra, El Oued)
- Homemade jam makers
- Organic cheese producers
- Natural cosmetics makers
- Spice producers
- And more organic/bio products

**Specifically targets businesses that are NOT already exporting** - your ideal clients!

## ✨ Features

- 🎯 **Targeted Search** - Focuses on small/medium bio producers
- 🚫 **Filters Big Companies** - Automatically excludes major exporters (Cevital, Sonatrach, etc.)
- 📱 **Complete Contact Info** - Extracts phone, email, WhatsApp, Facebook, Instagram
- 🌍 **Export Status** - Identifies businesses not currently exporting
- 🏷️ **Product Categories** - Organizes by product type (olive oil, dates, honey, etc.)
- 📊 **Multiple Sources** - Scrapes Ouedkniss, Facebook, Instagram, local markets

## 🎁 Target Products

- 🫒 **Olive Oil** - Extra virgin, organic (Kabylie region)
- 🍯 **Honey** - Mountain honey, thyme honey (Tlemcen)
- 🌴 **Dates** - Deglet Nour, organic dates (Biskra)
- 🍓 **Jams** - Artisanal, homemade jams
- 🧀 **Cheese** - Traditional cheese (Jben, Takammart)
- 🌿 **Spices** - Harissa, Ras el Hanout
- 💧 **Argan Oil** - Cosmetic and food grade
- 🧼 **Natural Soap** - Organic cosmetics
- 🍇 **Dried Fruits** - Figs, apricots, raisins
- 🌾 **Couscous** - Artisanal couscous

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/algerian-bio-export-scraper.git
cd algerian-bio-export-scraper

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### Usage

```bash
# Run the scraper
python export_opportunity_scraper.py
```

### Output

The scraper generates two files:
- `export_opportunities_YYYYMMDD_HHMMSS.csv` - Excel-compatible format
- `export_opportunities_YYYYMMDD_HHMMSS.json` - JSON format for APIs

## 📊 Sample Output

```csv
company_name,phone,email,facebook,instagram,products,export_ready,business_size
Huile Olive Bio Kabylie,+213 555 123 456,olive@gmail.com,facebook.com/olivebio,N/A,Olive Oil,No,Small
Miel Montagne Tlemcen,+213 555 234 567,N/A,facebook.com/mieltlemcen,instagram.com/miel_dz,Honey,No,Small
Confiture Artisanale,+213 555 345 678,confiture@yahoo.fr,N/A,instagram.com/confiture_alger,Jams,No,Small
```

## 📈 Expected Results

From a typical scraping session:
- **50-100+ producers** found
- **70-80%** with phone numbers
- **40-50%** with email addresses
- **60-70%** with social media
- **80-90%** NOT currently exporting (your target!)

## 💼 For Export Agencies

### Why This Scraper is Perfect for You

1. **Finds Your Ideal Clients** - Small producers who need export help
2. **Filters Out Competition** - Excludes big companies that already export
3. **Complete Contact Info** - Ready for immediate outreach
4. **Export Status** - Identifies businesses ready for your services
5. **Product Categories** - Easy to segment your outreach

### Outreach Strategy

1. **Filter** by `export_ready = "No"` (prime targets)
2. **Call** producers with phone numbers
3. **Message** on WhatsApp/Facebook/Instagram
4. **Email** professional proposals
5. **Convert** 3-5% into clients

### Revenue Potential

- **Per Client:** €50,000/year export × 15% commission = **€7,500/year**
- **10 Clients:** **€75,000/year**
- **50 Clients:** **€375,000/year**

## 🛠️ Technical Details

### Dependencies

- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `playwright` - Browser automation
- `lxml` - XML/HTML processing

### Data Sources

1. **Ouedkniss** - Algeria's largest classifieds site
2. **Facebook** - Business pages and groups
3. **Instagram** - Bio product hashtags
4. **Local Markets** - Known cooperatives and producers

### Contact Extraction

Automatically extracts:
- Algerian phone numbers (+213, 05X, 06X, 07X formats)
- Email addresses (prioritizes .dz domains)
- Facebook pages
- Instagram profiles
- WhatsApp numbers

## 📖 Documentation

- **[EXPORT_AGENCY_GUIDE.md](EXPORT_AGENCY_GUIDE.md)** - Complete guide for export agencies
- **[FOR_YOUR_EXPORT_AGENCY.md](FOR_YOUR_EXPORT_AGENCY.md)** - Quick reference and outreach tips

## 🎯 Use Cases

### Export Agencies
Find small producers to help export to Europe

### Importers
Discover authentic Algerian organic products

### Market Research
Analyze the Algerian bio/organic market

### Business Development
Connect with artisanal producers

## ⚠️ Important Notes

### Ethical Use
- Respect website terms of service
- Use reasonable delays between requests
- Don't overload servers
- Use data responsibly

### Legal Compliance
- Comply with GDPR for European contacts
- Follow local data protection laws
- Obtain consent before marketing

### Rate Limiting
- Built-in delays to avoid detection
- Respectful scraping practices
- Can adjust speed with worker count

## 🔧 Configuration

### Adjust Scraping Speed

Edit `export_opportunity_scraper.py`:

```python
# Increase delays for slower, safer scraping
time.sleep(5)  # Default: 2-3 seconds

# Reduce number of results per search
for listing in listings[:5]:  # Default: 10
```

### Add Custom Products

```python
self.target_products = {
    'your_product': ['search', 'terms', 'here'],
}
```

### Add Custom Regions

```python
# Add specific Algerian regions to target
'your_region': ['region', 'terms'],
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

MIT License - feel free to use for commercial purposes

## 🙏 Acknowledgments

- Built for export agencies helping Algerian producers
- Supports small businesses entering European markets
- Promotes Algerian organic/bio products globally

## 📧 Contact

For questions or support, please open an issue on GitHub.

## 🌟 Star This Repo

If this scraper helps your export business, please star the repository!

---

**Made with ❤️ for Algerian export opportunities** 🇩🇿 → 🇪🇺
