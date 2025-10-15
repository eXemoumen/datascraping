# 📸 Visual Guide - What You'll See

## 🖥️ Dashboard Overview

```
╔═══════════════════════════════════════════════════════════════╗
║  EspaceAgro Scraper Dashboard                                 ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  📊 STATISTICS                                                ║
║  ┌──────────────┬──────────────┬──────────────┬─────────────┐║
║  │    Total     │   Checked    │  Unchecked   │    Today    │║
║  │     450      │     120      │     330      │     25      │║
║  └──────────────┴──────────────┴──────────────┴─────────────┘║
║                                                               ║
║  🎮 CONTROLS                                                  ║
║  ┌──────────────────┐  ┌─────────────────────────────────┐  ║
║  │ Start Scraping   │  │ Search: ___________________     │  ║
║  └──────────────────┘  └─────────────────────────────────┘  ║
║                                                               ║
║  📋 ANNOUNCEMENTS TABLE                                       ║
║  ┌──┬────────────────────┬───────┬──────────┬──────────┬───┐║
║  │✓ │ Title              │ Type  │ Location │ Products │ → │║
║  ├──┼────────────────────┼───────┼──────────┼──────────┼───┤║
║  │☑ │ Huile d'olive bio  │ Vente │ Alger    │ Olive    │ → │║
║  │☐ │ Dattes export      │ Vente │ Biskra   │ Dattes   │ → │║
║  │☐ │ Miel naturel       │ Vente │ Tlemcen  │ Miel     │ → │║
║  │☑ │ Fruits secs        │ Vente │ Oran     │ Fruits   │ → │║
║  │☐ │ Légumes bio        │ Vente │ Setif    │ Légumes  │ → │║
║  └──┴────────────────────┴───────┴──────────┴──────────┴───┘║
╚═══════════════════════════════════════════════════════════════╝
```

## 🎨 Color Coding

### Statistics Cards
```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ 🔵 BLUE      │  │ 🟢 GREEN     │  │ 🟡 YELLOW    │  │ 🟣 PURPLE    │
│   Total      │  │   Checked    │  │  Unchecked   │  │    Today     │
│    450       │  │     120      │  │     330      │  │     25       │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
```

### Table Rows
```
Normal Row (Unchecked):
┌──┬────────────────────┬───────┬──────────┬──────────┬───┐
│☐ │ Announcement Title │ Vente │ Alger    │ Products │ → │
└──┴────────────────────┴───────┴──────────┴──────────┴───┘
White background

Checked Row:
┌──┬────────────────────┬───────┬──────────┬──────────┬───┐
│☑ │ Announcement Title │ Vente │ Alger    │ Products │ → │
└──┴────────────────────┴───────┴──────────┴──────────┴───┘
🟢 Green background
```

## 🎬 User Actions

### 1. Starting Scraping

**Before Click:**
```
┌──────────────────┐
│ Start Scraping   │  ← Click here
└──────────────────┘
```

**During Scraping:**
```
┌──────────────────┐
│ Scraping...      │  ← Button disabled
└──────────────────┘

Backend Terminal:
📄 Scraping page 1/10
  ✓ NEW: Huile d'olive bio...
  ✓ NEW: Dattes export...
  ⏭️  Exists: Miel naturel...
⏳ Waiting 4.2s before next page...
```

**After Completion:**
```
┌──────────────────┐
│ Start Scraping   │  ← Button enabled again
└──────────────────┘

Alert: "Scraping completed successfully"
Table updates with new data
Stats update with new counts
```

### 2. Checking Announcements

**Before Check:**
```
┌──┬────────────────────┬───────┬──────────┬──────────┬───┐
│☐ │ Huile d'olive bio  │ Vente │ Alger    │ Olive    │ → │
└──┴────────────────────┴───────┴──────────┴──────────┴───┘
White background
```

**Click Checkbox:**
```
       ↓ Click here
┌──┬────────────────────┬───────┬──────────┬──────────┬───┐
│☐ │ Huile d'olive bio  │ Vente │ Alger    │ Olive    │ → │
└──┴────────────────────┴───────┴──────────┴──────────┴───┘
```

**After Check:**
```
┌──┬────────────────────┬───────┬──────────┬──────────┬───┐
│☑ │ Huile d'olive bio  │ Vente │ Alger    │ Olive    │ → │
└──┴────────────────────┴───────┴──────────┴──────────┴───┘
🟢 Green background

Stats Update:
Checked: 120 → 121
Unchecked: 330 → 329
```

### 3. Searching

**Type in Search Box:**
```
┌─────────────────────────────────┐
│ Search: olive                   │  ← Type here
└─────────────────────────────────┘
```

**Table Filters Instantly:**
```
Before:
┌──┬────────────────────┬───────┬──────────┬──────────┬───┐
│☐ │ Huile d'olive bio  │ Vente │ Alger    │ Olive    │ → │
│☐ │ Dattes export      │ Vente │ Biskra   │ Dattes   │ → │
│☐ │ Miel naturel       │ Vente │ Tlemcen  │ Miel     │ → │
└──┴────────────────────┴───────┴──────────┴──────────┴───┘

After (filtered):
┌──┬────────────────────┬───────┬──────────┬──────────┬───┐
│☐ │ Huile d'olive bio  │ Vente │ Alger    │ Olive    │ → │
└──┴────────────────────┴───────┴──────────┴──────────┴───┘
Only rows matching "olive" shown
```

### 4. Opening Announcements

**Click Link:**
```
┌──┬────────────────────┬───────┬──────────┬──────────┬───┐
│☐ │ Huile d'olive bio  │ Vente │ Alger    │ Olive    │ → │ ← Click
└──┴────────────────────┴───────┴──────────┴──────────┴───┘
```

**Opens in New Tab:**
```
🌐 New Browser Tab:
https://www.espaceagro.com/membres/esvoir.asp?id=698632
                         ^^^^^^^^ Fixed URL format!
```

## 📊 Statistics Updates

### Initial State (Empty Database)
```
┌──────────┬──────────┬──────────┬──────────┐
│  Total   │ Checked  │Unchecked │  Today   │
│    0     │    0     │    0     │    0     │
└──────────┴──────────┴──────────┴──────────┘
```

### After First Scraping
```
┌──────────┬──────────┬──────────┬──────────┐
│  Total   │ Checked  │Unchecked │  Today   │
│   400    │    0     │   400    │   400    │
└──────────┴──────────┴──────────┴──────────┘
```

### After Checking Some Items
```
┌──────────┬──────────┬──────────┬──────────┐
│  Total   │ Checked  │Unchecked │  Today   │
│   400    │   120    │   280    │   400    │
└──────────┴──────────┴──────────┴──────────┘
```

### After Second Scraping (Next Day)
```
┌──────────┬──────────┬──────────┬──────────┐
│  Total   │ Checked  │Unchecked │  Today   │
│   425    │   120    │   305    │    25    │
└──────────┴──────────┴──────────┴──────────┘
Only 25 new announcements added!
```

## 🖥️ Terminal Output

### Backend Terminal (api.py)
```
$ python api.py

 * Serving Flask app 'api'
 * Debug mode: on
WARNING: This is a development server.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit

INFO:werkzeug:127.0.0.1 - - [15/Oct/2025 10:30:15] "GET /api/announcements HTTP/1.1" 200 -
INFO:werkzeug:127.0.0.1 - - [15/Oct/2025 10:30:15] "GET /api/stats HTTP/1.1" 200 -
INFO:werkzeug:127.0.0.1 - - [15/Oct/2025 10:31:20] "POST /api/scrape HTTP/1.1" 200 -
```

### Frontend Terminal (npm run dev)
```
$ npm run dev

> frontend@0.1.0 dev
> next dev

  ▲ Next.js 15.0.0
  - Local:        http://localhost:3000
  - Environments: .env

 ✓ Starting...
 ✓ Ready in 2.3s
```

### Scraper Output (During Scraping)
```
=== Scraping EspaceAgro Algeria Announcements ===

📄 Scraping page 1/10
  ✓ NEW: Huile d'olive bio de qualité supérieure
  ✓ NEW: Dattes export en gros
  ⏭️  Exists: Miel naturel
  ✓ NEW: Fruits secs variés
⏳ Waiting 4.2s before next page...

📄 Scraping page 2/10
  ⏭️  Exists: Légumes bio
  ✓ NEW: Épices traditionnelles
  ⏭️  Exists: Huile d'argan
⏳ Waiting 5.1s before next page...

✓ Total announcements scraped: 25
✓ Saved 25 listings to espaceagro_algeria_20251015_103045.csv
✓ Saved to espaceagro_algeria_20251015_103045.json
```

## 🎯 Visual Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    DAILY WORKFLOW                           │
└─────────────────────────────────────────────────────────────┘

1. START CHROME
   ┌──────────────────┐
   │ Chrome (Debug)   │
   │ Port: 9222       │
   │ Logged in ✓      │
   └──────────────────┘

2. START BACKEND
   ┌──────────────────┐
   │ Flask API        │
   │ Port: 5000       │
   │ Running ✓        │
   └──────────────────┘

3. START FRONTEND
   ┌──────────────────┐
   │ Next.js          │
   │ Port: 3000       │
   │ Running ✓        │
   └──────────────────┘

4. OPEN DASHBOARD
   ┌──────────────────┐
   │ Browser          │
   │ localhost:3000   │
   │ Dashboard ✓      │
   └──────────────────┘

5. SCRAPE DATA
   ┌──────────────────┐
   │ Click Button     │
   │ Wait...          │
   │ Complete ✓       │
   └──────────────────┘

6. REVIEW & CHECK
   ┌──────────────────┐
   │ Browse Table     │
   │ Check Boxes      │
   │ Done ✓           │
   └──────────────────┘
```

## 🎨 Responsive Design

### Desktop View (Wide Screen)
```
┌─────────────────────────────────────────────────────────────┐
│  Stats: [Total] [Checked] [Unchecked] [Today]              │
│  Controls: [Button] [Search________________________]        │
│  Table: [✓][Title___________][Type][Location][Products][→] │
└─────────────────────────────────────────────────────────────┘
```

### Tablet View (Medium Screen)
```
┌──────────────────────────────────────┐
│  Stats: [Total] [Checked]            │
│         [Unchecked] [Today]          │
│  Controls: [Button]                  │
│            [Search______________]    │
│  Table: [✓][Title_____][Type][→]    │
└──────────────────────────────────────┘
```

### Mobile View (Small Screen)
```
┌────────────────────┐
│  Stats:            │
│  [Total]           │
│  [Checked]         │
│  [Unchecked]       │
│  [Today]           │
│  [Button]          │
│  [Search______]    │
│  Table:            │
│  [✓][Title___][→]  │
└────────────────────┘
```

---

**Visual guide complete!** 📸

Now you know exactly what to expect when using the dashboard!
