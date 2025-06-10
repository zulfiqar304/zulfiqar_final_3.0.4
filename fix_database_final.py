
from main import app, db
from sqlalchemy import text

def fix_database_final():
    """Complete database fix for all missing columns and issues"""
    with app.app_context():
        print("🔧 Starting comprehensive database fix...")
        
        try:
            # Fix ad_watch_session table
            print("\n📋 Fixing ad_watch_session table...")
            result = db.engine.execute(text("PRAGMA table_info(ad_watch_session)"))
            existing_columns = [row[1] for row in result]
            print(f"Current ad_watch_session columns: {existing_columns}")
            
            ad_columns_to_add = [
                ('direct_ads_watched_count', 'INTEGER DEFAULT 0'),
                ('last_direct_ad_time', 'DATETIME'),
                ('direct_cooldown_until', 'DATETIME')
            ]
            
            for column_name, column_def in ad_columns_to_add:
                if column_name not in existing_columns:
                    try:
                        db.engine.execute(text(f'ALTER TABLE ad_watch_session ADD COLUMN {column_name} {column_def}'))
                        print(f"✅ Added column: {column_name}")
                    except Exception as e:
                        print(f"❌ Error adding column {column_name}: {e}")
                else:
                    print(f"✅ Column {column_name} already exists")
            
            # Update existing records to have default values
            try:
                db.engine.execute(text("UPDATE ad_watch_session SET direct_ads_watched_count = 0 WHERE direct_ads_watched_count IS NULL"))
                print("✅ Updated NULL direct_ads_watched_count values")
            except Exception as e:
                print(f"⚠️ Could not update NULL values: {e}")
            
            print("✅ ad_watch_session table fix completed!")
            
            # Verify tables
            print("\n📊 Verifying database structure...")
            
            # Check ad_watch_session final structure
            result = db.engine.execute(text("PRAGMA table_info(ad_watch_session)"))
            final_columns = [row[1] for row in result]
            print(f"✅ Final ad_watch_session columns: {final_columns}")
            
            print("\n🎉 Database fix completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during database fix: {e}")

if __name__ == "__main__":
    fix_database_final()
