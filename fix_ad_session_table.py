
from main import app, db
from sqlalchemy import text

def fix_ad_session_table():
    """Add missing columns to ad_watch_session table"""
    with app.app_context():
        try:
            # Check if columns exist first
            result = db.engine.execute(text("PRAGMA table_info(ad_watch_session)"))
            existing_columns = [row[1] for row in result]
            print(f"Current columns: {existing_columns}")
            
            # Add missing columns one by one
            columns_to_add = [
                ('direct_ads_watched_count', 'INTEGER DEFAULT 0'),
                ('last_direct_ad_time', 'DATETIME'),
                ('direct_cooldown_until', 'DATETIME')
            ]
            
            for column_name, column_def in columns_to_add:
                if column_name not in existing_columns:
                    try:
                        db.engine.execute(text(f'ALTER TABLE ad_watch_session ADD COLUMN {column_name} {column_def}'))
                        print(f"✅ Added column: {column_name}")
                    except Exception as e:
                        if "duplicate column name" in str(e).lower():
                            print(f"✅ Column {column_name} already exists")
                        else:
                            print(f"❌ Error adding column {column_name}: {e}")
                else:
                    print(f"✅ Column {column_name} already exists")
                    
            print("✅ AdWatchSession table updated successfully!")
            
        except Exception as e:
            print(f"❌ Error fixing ad_watch_session table: {e}")

if __name__ == "__main__":
    fix_ad_session_table()
