#!/usr/bin/env python3
"""Quick test to see what's in the database"""

import sqlite3

conn = sqlite3.connect('espaceagro.db')
cursor = conn.cursor()

# Get total count
cursor.execute('SELECT COUNT(*) FROM announcements')
total = cursor.fetchone()[0]
print(f"📊 Total announcements in database: {total}")

# Get unique member IDs
cursor.execute('SELECT COUNT(DISTINCT member_id) FROM announcements')
unique = cursor.fetchone()[0]
print(f"🆔 Unique member IDs: {unique}")

# Get sample of latest
cursor.execute('SELECT announcement_title, created_at FROM announcements ORDER BY created_at DESC LIMIT 5')
print(f"\n📋 Latest 5 announcements:")
for row in cursor.fetchall():
    print(f"  - {row[0][:60]} ({row[1]})")

# Check for duplicates
cursor.execute('SELECT member_id, COUNT(*) as count FROM announcements GROUP BY member_id HAVING count > 1')
duplicates = cursor.fetchall()
if duplicates:
    print(f"\n⚠️  Found {len(duplicates)} duplicate member_ids!")
else:
    print(f"\n✅ No duplicates found")

conn.close()
