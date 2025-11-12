"""
Migration script to add parent_id column to comments table for nested replies
Run: python add_parent_id_to_comments.py
"""

import sqlite3
import os

DATABASE_URL = os.path.join(os.path.dirname(__file__), "instagram_clone.db")

try:
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()

    print(f"Connecting to database: {DATABASE_URL}")

    # Check if parent_id column exists
    cursor.execute("PRAGMA table_info(comments)")
    columns = [col[1] for col in cursor.fetchall()]

    if 'parent_id' not in columns:
        print("Adding parent_id column to comments table...")
        cursor.execute("ALTER TABLE comments ADD COLUMN parent_id INTEGER")
        
        # Create index on parent_id for better query performance
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_comments_parent_id ON comments(parent_id)")
        
        conn.commit()
        print("[SUCCESS] Successfully added parent_id column!")
        print("[SUCCESS] Created index on parent_id")
    else:
        print("[INFO] parent_id column already exists")
    
    # Display table structure
    cursor.execute("PRAGMA table_info(comments)")
    columns = cursor.fetchall()
    print("\n[TABLE STRUCTURE] Current comments table structure:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    conn.close()
    print("\n[SUCCESS] Migration complete!")
    
except Exception as e:
    print(f"[ERROR] Error: {e}")
    if conn:
        conn.rollback()
        conn.close()

