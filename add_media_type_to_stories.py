"""
Database migration script to add media_type column to stories table
Run this script from the backend directory: python add_media_type_to_stories.py
"""

import sqlite3
import os

# Get database path
db_path = os.path.join(os.path.dirname(__file__), "instagram_clone.db")

print(f"Connecting to database: {db_path}")

try:
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if media_type column exists
    cursor.execute("PRAGMA table_info(stories)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'media_type' not in columns:
        print("Adding media_type column to stories table...")
        
        # Add media_type column with default value 'image'
        cursor.execute("""
            ALTER TABLE stories 
            ADD COLUMN media_type VARCHAR(10) DEFAULT 'image' NOT NULL
        """)
        
        # Update existing stories to have media_type='image'
        cursor.execute("""
            UPDATE stories 
            SET media_type = 'image' 
            WHERE media_type IS NULL OR media_type = ''
        """)
        
        conn.commit()
        print("[SUCCESS] Successfully added media_type column!")
        print("[SUCCESS] All existing stories set to media_type='image'")
    else:
        print("[INFO] media_type column already exists")
    
    # Display table structure
    cursor.execute("PRAGMA table_info(stories)")
    columns = cursor.fetchall()
    print("\n[TABLE STRUCTURE] Current stories table structure:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    conn.close()
    print("\n[SUCCESS] Migration complete!")
    
except Exception as e:
    print(f"[ERROR] Error: {e}")
    if conn:
        conn.rollback()
        conn.close()

