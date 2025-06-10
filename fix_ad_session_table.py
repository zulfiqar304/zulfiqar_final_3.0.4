
from main import app, db, AdWatchSession

def fix_ad_session_table():
    """Add missing columns to ad_watch_session table"""
    with app.app_context():
        try:
            # Add missing columns using raw SQL
            db.engine.execute('ALTER TABLE ad_watch_session ADD COLUMN direct_ads_watched_count INTEGER DEFAULT 0')
            db.engine.execute('ALTER TABLE ad_watch_session ADD COLUMN last_direct_ad_time DATETIME')
            db.engine.execute('ALTER TABLE ad_watch_session ADD COLUMN direct_cooldown_until DATETIME')
            print("✅ Added missing columns to ad_watch_session table")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("✅ Columns already exist in ad_watch_session table")
            else:
                print(f"❌ Error adding columns: {e}")

if __name__ == "__main__":
    fix_ad_session_table()
