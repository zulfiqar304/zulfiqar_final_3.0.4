
from main import app, db, User, Order
from sqlalchemy import inspect, text

def check_and_fix_database():
    """Comprehensive check and fix for all database issues"""
    with app.app_context():
        try:
            print("🔍 Starting comprehensive database check...")
            
            # Get database inspector
            inspector = inspect(db.engine)
            
            # Check all tables exist
            existing_tables = inspector.get_table_names()
            print(f"📋 Existing tables: {existing_tables}")
            
            # Expected tables
            expected_tables = [
                'user', 'order', 'selected_service', 'coin_configuration', 
                'coin_transaction', 'ad_watch_session', 'announcement', 
                'password_reset_token', 'spin_wheel', 'user_referral', 
                'referral_reward', 'device_registration', 'admin_spin_grant', 
                'page_visit', 'home_page_content'
            ]
            
            missing_tables = [table for table in expected_tables if table not in existing_tables]
            if missing_tables:
                print(f"⚠️  Missing tables: {missing_tables}")
                print("🔨 Creating missing tables...")
                db.create_all()
                print("✅ Missing tables created")
            else:
                print("✅ All expected tables exist")
            
            # Check Order table columns specifically
            order_columns = [col['name'] for col in inspector.get_columns('order')]
            print(f"📋 Order table columns: {order_columns}")
            
            required_order_columns = [
                'id', 'user_id', 'service_id', 'service_name', 'link', 
                'quantity', 'coins_required', 'status', 'jap_order_id', 
                'created_at', 'start_count', 'remains', 'completion_time',
                'last_status_update'
            ]
            
            missing_order_columns = [col for col in required_order_columns if col not in order_columns]
            if missing_order_columns:
                print(f"⚠️  Missing Order columns: {missing_order_columns}")
                
                # Add missing columns
                for column in missing_order_columns:
                    try:
                        if column == 'last_status_update':
                            with db.engine.connect() as connection:
                                connection.execute(text('ALTER TABLE "order" ADD COLUMN last_status_update DATETIME DEFAULT CURRENT_TIMESTAMP'))
                                connection.commit()
                        elif column == 'completion_time':
                            with db.engine.connect() as connection:
                                connection.execute(text('ALTER TABLE "order" ADD COLUMN completion_time VARCHAR(50)'))
                                connection.commit()
                        elif column == 'start_count':
                            with db.engine.connect() as connection:
                                connection.execute(text('ALTER TABLE "order" ADD COLUMN start_count INTEGER DEFAULT 0'))
                                connection.commit()
                        elif column == 'remains':
                            with db.engine.connect() as connection:
                                connection.execute(text('ALTER TABLE "order" ADD COLUMN remains INTEGER DEFAULT 0'))
                                connection.commit()
                        print(f"✅ Added column: {column}")
                    except Exception as e:
                        print(f"⚠️  Could not add column {column}: {e}")
            else:
                print("✅ All Order table columns exist")
            
            # Update NULL last_status_update values
            try:
                with db.engine.connect() as connection:
                    connection.execute(text('UPDATE "order" SET last_status_update = created_at WHERE last_status_update IS NULL'))
                    connection.commit()
                print("✅ Updated NULL last_status_update values")
            except Exception as e:
                print(f"⚠️  Could not update last_status_update values: {e}")
            
            # Check User table columns
            user_columns = [col['name'] for col in inspector.get_columns('user')]
            expected_user_columns = [
                'id', 'username', 'email', 'password', 'coins', 
                'last_login_date', 'is_admin', 'is_banned', 
                'referral_code', 'referred_by'
            ]
            
            missing_user_columns = [col for col in expected_user_columns if col not in user_columns]
            if missing_user_columns:
                print(f"⚠️  Missing User columns: {missing_user_columns}")
            else:
                print("✅ All User table columns exist")
            
            # Test database operations
            print("🧪 Testing database operations...")
            
            # Test user query
            try:
                user_count = User.query.count()
                print(f"✅ User table accessible - {user_count} users")
            except Exception as e:
                print(f"❌ User table error: {e}")
            
            # Test order query
            try:
                order_count = Order.query.count()
                print(f"✅ Order table accessible - {order_count} orders")
            except Exception as e:
                print(f"❌ Order table error: {e}")
                
            print("🎉 Database check completed!")
            
        except Exception as e:
            print(f"❌ Critical error during database check: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    check_and_fix_database()
