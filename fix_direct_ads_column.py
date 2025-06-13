
import sqlite3
from datetime import datetime

def fix_direct_ads_column():
    """Add missing direct_ads_watched_count column to ad_watch_session table"""
    try:
        # Connect to the database
        conn = sqlite3.connect('instance/users.db')
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("PRAGMA table_info(ad_watch_session)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        if 'direct_ads_watched_count' not in column_names:
            print("Adding direct_ads_watched_count column...")
            cursor.execute("""
                ALTER TABLE ad_watch_session 
                ADD COLUMN direct_ads_watched_count INTEGER DEFAULT 0
            """)
            print("✅ direct_ads_watched_count column added successfully!")
        else:
            print("✅ direct_ads_watched_count column already exists!")
        
        if 'last_direct_ad_time' not in column_names:
            print("Adding last_direct_ad_time column...")
            cursor.execute("""
                ALTER TABLE ad_watch_session 
                ADD COLUMN last_direct_ad_time DATETIME
            """)
            print("✅ last_direct_ad_time column added successfully!")
        else:
            print("✅ last_direct_ad_time column already exists!")
            
        if 'direct_cooldown_until' not in column_names:
            print("Adding direct_cooldown_until column...")
            cursor.execute("""
                ALTER TABLE ad_watch_session 
                ADD COLUMN direct_cooldown_until DATETIME
            """)
            print("✅ direct_cooldown_until column added successfully!")
        else:
            print("✅ direct_cooldown_until column already exists!")
        
        # Commit changes and close connection
        conn.commit()
        conn.close()
        
        print("🎉 Database fix completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        return False

if __name__ == "__main__":
    fix_direct_ads_column()
