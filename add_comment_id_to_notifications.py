"""
Migration script to add comment_id column to notifications table
Run: python add_comment_id_to_notifications.py
"""

import sqlite3
import os

DATABASE_URL = os.path.join(os.path.dirname(__file__), "instagram_clone.db")

try:
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()

    print(f"Connecting to database: {DATABASE_URL}")

    # Check if comment_id column exists
    cursor.execute("PRAGMA table_info(notifications)")
    columns = [col[1] for col in cursor.fetchall()]

    if 'comment_id' not in columns:
        print("Adding comment_id column to notifications table...")
        cursor.execute("ALTER TABLE notifications ADD COLUMN comment_id INTEGER")
        
        conn.commit()
        print("[SUCCESS] Successfully added comment_id column!")
    else:
        print("[INFO] comment_id column already exists")
    
    # Display table structure
    cursor.execute("PRAGMA table_info(notifications)")
    columns = cursor.fetchall()
    print("\n[TABLE STRUCTURE] Current notifications table structure:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    conn.close()
    print("\n[SUCCESS] Migration complete!")
    
except Exception as e:
    print(f"[ERROR] Error: {e}")
    if conn:
        conn.rollback()
        conn.close()

