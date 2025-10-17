#!/usr/bin/env python3
"""
Flask API for EspaceAgro Scraper - Production Version
Works without Chrome/Selenium (read-only mode for deployed version)
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os
import logging

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use PostgreSQL in production, SQLite in development
DATABASE_URL = os.getenv('DATABASE_URL', 'espaceagro.db')
IS_PRODUCTION = 'DATABASE_URL' in os.environ

def get_db_connection():
    """Get database connection"""
    if IS_PRODUCTION:
        # PostgreSQL connection
        import psycopg2
        from psycopg2.extras import RealDictCursor
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    else:
        # SQLite connection
        conn = sqlite3.connect('espaceagro.db')
        conn.row_factory = sqlite3.Row
        return conn


def init_database():
    """Initialize database schema"""
    if IS_PRODUCTION:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS announcements (
                id SERIAL PRIMARY KEY,
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
    else:
        conn = sqlite3.connect('espaceagro.db')
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


@app.route('/api/announcements', methods=['GET'])
def get_announcements():
    """Get all announcements"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM announcements 
            ORDER BY created_at DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        announcements = [dict(row) for row in rows]
        return jsonify(announcements)
    except Exception as e:
        logger.error(f"Error fetching announcements: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/announcements/<int:announcement_id>/check', methods=['PUT'])
def toggle_check(announcement_id):
    """Toggle checked status of an announcement"""
    try:
        data = request.json
        checked = data.get('checked', 0)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE announcements 
            SET checked = %s 
            WHERE id = %s
        ''' if IS_PRODUCTION else '''
            UPDATE announcements 
            SET checked = ? 
            WHERE id = ?
        ''', (checked, announcement_id))
        conn.commit()
        conn.close()
        
        return jsonify({"success": True, "checked": checked})
    except Exception as e:
        logger.error(f"Error updating announcement: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/scrape', methods=['POST'])
def start_scraping():
    """Start scraping process - disabled in production"""
    if IS_PRODUCTION:
        return jsonify({
            "error": "Scraping is disabled in production. Please run the scraper locally and sync the database."
        }), 403
    
    # Local scraping logic here (same as before)
    return jsonify({"message": "Scraping not available in production"}), 403


@app.route('/api/scrape/status', methods=['GET'])
def get_scraping_status():
    """Get current scraping status"""
    return jsonify({
        "running": False, 
        "message": "Scraping is disabled in production mode"
    })


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if IS_PRODUCTION:
            cursor.execute('SELECT COUNT(*) as total FROM announcements')
            total = cursor.fetchone()['total']
            
            cursor.execute('SELECT COUNT(*) as checked FROM announcements WHERE checked = 1')
            checked = cursor.fetchone()['checked']
            
            cursor.execute('SELECT COUNT(*) as today FROM announcements WHERE DATE(created_at) = CURRENT_DATE')
            today = cursor.fetchone()['today']
        else:
            cursor.execute('SELECT COUNT(*) as total FROM announcements')
            total = cursor.fetchone()['total']
            
            cursor.execute('SELECT COUNT(*) as checked FROM announcements WHERE checked = 1')
            checked = cursor.fetchone()['checked']
            
            cursor.execute('SELECT COUNT(*) as today FROM announcements WHERE DATE(created_at) = DATE("now")')
            today = cursor.fetchone()['today']
        
        conn.close()
        
        return jsonify({
            "total": total,
            "checked": checked,
            "unchecked": total - checked,
            "today": today
        })
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "mode": "production" if IS_PRODUCTION else "development"})


# Initialize database on startup
init_database()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=not IS_PRODUCTION)
