# 🏗️ System Architecture

## Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         USER                                │
│                    (Web Browser)                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTP Requests
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                   FRONTEND                                  │
│                   (Next.js)                                 │
│                 Port: 3000                                  │
│                                                             │
│  Components:                                                │
│  • Dashboard Stats                                          │
│  • Scraping Controls                                        │
│  • Data Table                                               │
│  • Search/Filter                                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ REST API Calls
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND                                  │
│                   (Flask API)                               │
│                  Port: 5000                                 │
│                                                             │
│  Endpoints:                                                 │
│  • GET  /api/announcements                                  │
│  • GET  /api/stats                                          │
│  • POST /api/scrape                                         │
│  • GET  /api/scrape/status                                  │
│  • PUT  /api/announcements/:id/check                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ SQL Queries
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                   DATABASE                                  │
│                   (SQLite)                                  │
│              File: espaceagro.db                            │
│                                                             │
│  Table: announcements                                       │
│  • id (PRIMARY KEY)                                         │
│  • member_id (UNIQUE)                                       │
│  • announcement_title                                       │
│  • description                                              │
│  • products                                                 │
│  • location                                                 │
│  • announcement_url                                         │
│  • checked (0 or 1)                                         │
│  • created_at                                               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Read/Write
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                    SCRAPER                                  │
│              (Python + Selenium)                            │
│                                                             │
│  Process:                                                   │
│  1. Connect to Chrome (debug mode)                          │
│  2. Navigate to espaceagro.com                              │
│  3. Extract announcement data                               │
│  4. Check for duplicates                                    │
│  5. Save new items to database                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Remote Debugging Protocol
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                    CHROME                                   │
│              (Debug Mode: Port 9222)                        │
│                                                             │
│  • User logged in to espaceagro.com                         │
│  • Maintains session cookies                                │
│  • Controlled by Selenium                                   │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. User Starts Scraping

```
User clicks "Start Scraping"
    ↓
Frontend sends POST to /api/scrape
    ↓
Backend starts scraper in background thread
    ↓
Scraper connects to Chrome (port 9222)
    ↓
Scraper navigates to espaceagro.com
    ↓
Scraper extracts data from each page
    ↓
For each announcement:
    ↓
    Check if member_id exists in database
    ↓
    If NEW → Insert into database
    ↓
    If EXISTS → Skip
    ↓
Backend updates scraping status
    ↓
Frontend polls /api/scrape/status
    ↓
When complete, frontend refreshes data
    ↓
User sees updated table
```

### 2. User Checks Announcement

```
User clicks checkbox
    ↓
Frontend sends PUT to /api/announcements/:id/check
    ↓
Backend updates checked field in database
    ↓
Backend returns success
    ↓
Frontend updates UI (green background)
    ↓
Frontend refreshes stats
```

### 3. User Searches

```
User types in search box
    ↓
Frontend filters announcements locally
    ↓
Table updates in real-time
    ↓
(No backend call needed)
```

## Component Details

### Frontend (Next.js)

**File:** `frontend/app/page.tsx`

**State Management:**
```typescript
- announcements: Announcement[]
- stats: Stats
- loading: boolean
- scraping: boolean
- searchTerm: string
```

**Key Functions:**
```typescript
- fetchAnnouncements()  // Get all data
- fetchStats()          // Get statistics
- toggleCheck()         // Toggle checkbox
- startScraping()       // Start scraping
- filteredAnnouncements // Search filter
```

### Backend (Flask)

**File:** `api.py`

**Routes:**
```python
GET  /api/announcements        # Get all announcements
GET  /api/stats                # Get statistics
POST /api/scrape               # Start scraping
GET  /api/scrape/status        # Get scraping status
PUT  /api/announcements/:id/check  # Toggle checked
```

**Key Functions:**
```python
- get_db_connection()   # Database connection
- get_announcements()   # Query all records
- toggle_check()        # Update checked status
- start_scraping()      # Run scraper in thread
- get_stats()           # Calculate statistics
```

### Database (SQLite)

**File:** `espaceagro.db`

**Schema:**
```sql
CREATE TABLE announcements (
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
);
```

**Indexes:**
```sql
UNIQUE INDEX on member_id  # Prevents duplicates
INDEX on checked           # Fast filtering
INDEX on created_at        # Fast date queries
```

### Scraper (Python + Selenium)

**File:** `espaceagro_scraper.py`

**Key Methods:**
```python
- __init__()                    # Initialize with database
- _init_database()              # Create schema
- connect_to_chrome()           # Connect to debug Chrome
- scrape_algeria_announcements() # Main scraping loop
- _extract_announcements()      # Parse page HTML
- _parse_listing()              # Extract announcement data
- _announcement_exists()        # Check for duplicates
- _save_to_database()           # Insert new record
```

**Process:**
```python
1. Connect to Chrome (port 9222)
2. For each page (1 to max_pages):
   a. Navigate to URL
   b. Wait for page load
   c. Parse HTML with BeautifulSoup
   d. Extract announcements
   e. For each announcement:
      - Check if exists (by member_id)
      - If new, save to database
      - If exists, skip
   f. Random delay (3-6 seconds)
3. Close connection
```

## Technology Stack

### Frontend
- **Framework:** Next.js 15
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **HTTP Client:** Fetch API
- **Port:** 3000

### Backend
- **Framework:** Flask 3.0
- **Language:** Python 3.x
- **CORS:** Flask-CORS
- **Threading:** Python threading
- **Port:** 5000

### Database
- **Engine:** SQLite 3
- **ORM:** None (raw SQL)
- **File:** espaceagro.db
- **Size:** ~1MB per 1000 records

### Scraper
- **Browser:** Chrome (debug mode)
- **Automation:** Selenium WebDriver
- **Parser:** BeautifulSoup4
- **Protocol:** Chrome DevTools Protocol
- **Port:** 9222

## Deployment Options

### Development (Current)
```
Frontend: npm run dev (localhost:3000)
Backend:  python api.py (localhost:5000)
Database: SQLite file
Chrome:   Local debug mode
```

### Production Option 1 (Simple)
```
Frontend: Vercel (free)
Backend:  Railway/Render (free tier)
Database: PostgreSQL (Railway/Render)
Chrome:   Not needed (use Playwright)
```

### Production Option 2 (Advanced)
```
Frontend: AWS Amplify / Netlify
Backend:  AWS Lambda / Google Cloud Run
Database: AWS RDS / Google Cloud SQL
Chrome:   AWS Lambda with Chromium layer
```

### Production Option 3 (Self-hosted)
```
Frontend: Nginx + PM2
Backend:  Gunicorn + Nginx
Database: PostgreSQL
Chrome:   Headless Chrome
All:      Docker containers
```

## Security Considerations

### Current (Development)
- ⚠️ No authentication
- ⚠️ CORS open to all
- ⚠️ No rate limiting
- ⚠️ No encryption
- ⚠️ SQLite (single user)

### Production Recommendations
- ✅ Add JWT authentication
- ✅ Restrict CORS to frontend domain
- ✅ Add rate limiting (Flask-Limiter)
- ✅ Use HTTPS everywhere
- ✅ Migrate to PostgreSQL
- ✅ Add API keys
- ✅ Validate all inputs
- ✅ Add logging/monitoring

## Performance

### Current Capacity
- **Scraping:** ~400 announcements per session
- **Database:** Can handle 100,000+ records
- **Frontend:** Renders 500+ rows smoothly
- **API:** ~100 requests/second

### Bottlenecks
1. **Scraping speed:** Limited by page load time
2. **SQLite:** Single writer at a time
3. **Frontend:** Large tables may slow down

### Optimizations
1. **Pagination:** Add pagination to table
2. **Caching:** Cache stats in Redis
3. **Indexing:** Add database indexes
4. **Lazy loading:** Load table rows on scroll
5. **PostgreSQL:** For concurrent writes

## Monitoring

### Logs
- **Frontend:** Browser console
- **Backend:** Terminal output
- **Scraper:** Terminal output
- **Database:** No logs (SQLite)

### Metrics to Track
- Scraping success rate
- New announcements per day
- API response times
- Database size
- Error rates

### Recommended Tools
- **Sentry:** Error tracking
- **LogRocket:** Frontend monitoring
- **Prometheus:** Metrics collection
- **Grafana:** Dashboards

---

**Architecture designed for simplicity and efficiency!** 🏗️
