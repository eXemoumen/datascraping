#!/usr/bin/env python3
"""
Flask API for EspaceAgro Scraper
Provides REST endpoints for the Next.js frontend
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import subprocess
import threading
import logging

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = "espaceagro.db"
scraping_status = {"running": False, "message": ""}


def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


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
    """Start scraping process"""
    global scraping_status
    
    if scraping_status["running"]:
        return jsonify({"error": "Scraping already in progress"}), 400
    
    def run_scraper():
        global scraping_status
        try:
            scraping_status = {"running": True, "message": "Scraping in progress..."}
            result = subprocess.run(
                ['python', 'espaceagro_scraper.py'],
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode == 0:
                scraping_status = {"running": False, "message": "Scraping completed successfully"}
            else:
                scraping_status = {"running": False, "message": f"Scraping failed: {result.stderr}"}
        except Exception as e:
            scraping_status = {"running": False, "message": f"Error: {str(e)}"}
    
    thread = threading.Thread(target=run_scraper)
    thread.start()
    
    return jsonify({"success": True, "message": "Scraping started"})


@app.route('/api/scrape/status', methods=['GET'])
def get_scraping_status():
    """Get current scraping status"""
    return jsonify(scraping_status)


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
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


if __name__ == '__main__':
    app.run(debug=True, port=5001, host='127.0.0.1')
