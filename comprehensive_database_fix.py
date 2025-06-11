
from main import app, db, User, CoinConfiguration, AdWatchSession
from sqlalchemy import text, inspect
from datetime import datetime

def comprehensive_database_fix():
    """Complete database check and fix for all issues"""
    with app.app_context():
        print("🔧 Starting comprehensive database fix...")
        
        try:
            # Ensure all tables exist
            print("\n📋 Creating all tables...")
            db.create_all()
            print("✅ All tables created/verified")
            
            # Fix ad_watch_session table columns
            print("\n🔧 Checking ad_watch_session table...")
            inspector = inspect(db.engine)
            ad_columns = [col['name'] for col in inspector.get_columns('ad_watch_session')]
            print(f"Current columns: {ad_columns}")
            
            # Add missing columns to ad_watch_session
            missing_ad_columns = [
                ('direct_ads_watched_count', 'INTEGER DEFAULT 0'),
                ('last_direct_ad_time', 'DATETIME'),
                ('direct_cooldown_until', 'DATETIME')
            ]
            
            for column_name, column_def in missing_ad_columns:
                if column_name not in ad_columns:
                    try:
                        db.engine.execute(text(f'ALTER TABLE ad_watch_session ADD COLUMN {column_name} {column_def}'))
                        print(f"✅ Added missing column: {column_name}")
                    except Exception as e:
                        print(f"⚠️ Column {column_name} might already exist: {e}")
                else:
                    print(f"✅ Column {column_name} exists")
            
            # Update NULL values
            try:
                db.engine.execute(text("UPDATE ad_watch_session SET direct_ads_watched_count = 0 WHERE direct_ads_watched_count IS NULL"))
                print("✅ Updated NULL direct_ads_watched_count values")
            except:
                pass
            
            # Ensure essential coin configurations exist
            print("\n💰 Checking coin configurations...")
            essential_configs = [
                ('daily_login_bonus', 5, 'Daily login reward for active users'),
                ('ad_watch_reward', 0.5, 'Reward for watching ads (both types)'),
                ('registration_bonus', 5, 'Welcome bonus for new users'),
                ('login_bonus_activity_days', 3, 'Days to check for activity before login bonus'),
                ('min_ads_for_login_bonus', 1, 'Minimum ads required for login bonus'),
                ('pkr_to_coins_rate', 2, 'PKR to coins conversion rate'),
                ('easypaisa_account_name', 0, 'Zulfiqar Ali'),
                ('easypaisa_account_number', 0, '+92-343-3662304'),
                ('jap_api_url', 0, 'https://justanotherpanel.com/api/v2'),
                ('jap_api_key', 0, 'c88871268f8d5276927ff8c09fceb422')
            ]
            
            for config_name, value, desc in essential_configs:
                existing = CoinConfiguration.query.filter_by(config_name=config_name).first()
                if not existing:
                    new_config = CoinConfiguration(
                        config_name=config_name,
                        coin_value=value,
                        description=desc,
                        is_active=True
                    )
                    db.session.add(new_config)
                    print(f"✅ Added config: {config_name}")
                else:
                    print(f"✅ Config exists: {config_name}")
            
            # Create admin user if doesn't exist
            print("\n👤 Checking admin user...")
            admin_user = User.query.filter_by(is_admin=True).first()
            if not admin_user:
                from werkzeug.security import generate_password_hash
                admin = User(
                    username='admin',
                    email='admin@zmworld.com',
                    password=generate_password_hash('MechEnergy7130@'),
                    is_admin=True,
                    coins=10000,
                    referral_code='ADMIN001'
                )
                db.session.add(admin)
                print("✅ Created admin user")
            else:
                print("✅ Admin user exists")
            
            # Commit all changes
            db.session.commit()
            print("\n🎉 Database fix completed successfully!")
            
            # Verify final state
            print("\n📊 Final verification...")
            total_users = User.query.count()
            total_configs = CoinConfiguration.query.count()
            admin_count = User.query.filter_by(is_admin=True).count()
            
            print(f"✅ Total users: {total_users}")
            print(f"✅ Total configurations: {total_configs}")
            print(f"✅ Admin users: {admin_count}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during fix: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = comprehensive_database_fix()
    if success:
        print("\n🎉 All fixes applied successfully!")
    else:
        print("\n❌ Some errors occurred during fix")
