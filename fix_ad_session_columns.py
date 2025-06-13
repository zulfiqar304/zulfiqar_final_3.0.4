
from main import app, db
from sqlalchemy import text

def fix_ad_session_columns():
    """Add missing columns to ad_watch_session table"""
    with app.app_context():
        try:
            # Check if columns exist and add them if missing
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('ad_watch_session')]
            
            missing_columns = []
            required_columns = {
                'direct_ads_watched_count': 'INTEGER DEFAULT 0',
                'last_direct_ad_time': 'DATETIME',
                'direct_cooldown_until': 'DATETIME'
            }
            
            for col_name, col_type in required_columns.items():
                if col_name not in columns:
                    missing_columns.append((col_name, col_type))
            
            if missing_columns:
                print(f"Adding missing columns: {[col[0] for col in missing_columns]}")
                
                for col_name, col_type in missing_columns:
                    try:
                        sql = f"ALTER TABLE ad_watch_session ADD COLUMN {col_name} {col_type}"
                        db.engine.execute(text(sql))
                        print(f"✅ Added column: {col_name}")
                    except Exception as e:
                        print(f"⚠️ Column {col_name} might already exist: {e}")
                
                print("✅ Database columns updated successfully!")
            else:
                print("✅ All required columns already exist!")
                
        except Exception as e:
            print(f"❌ Error fixing ad session columns: {e}")

if __name__ == "__main__":
    fix_ad_session_columns()
