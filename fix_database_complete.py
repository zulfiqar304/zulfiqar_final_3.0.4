
import sqlite3
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize Flask app for database context
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def fix_database():
    """Fix all database issues including missing columns"""
    
    # Get database path
    db_path = 'instance/users.db'
    
    # Create instance directory if it doesn't exist
    os.makedirs('instance', exist_ok=True)
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔧 Starting database repair...")
        
        # Check if user table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
        if not cursor.fetchone():
            print("❌ User table doesn't exist! Creating tables...")
            with app.app_context():
                db.create_all()
            print("✅ All tables created")
        
        # Get current user table structure
        cursor.execute('PRAGMA table_info(user)')
        existing_columns = [row[1] for row in cursor.fetchall()]
        print(f"📋 Current user table columns: {existing_columns}")
        
        # Define all required columns for user table
        required_columns = {
            'last_activity': 'ALTER TABLE user ADD COLUMN last_activity DATETIME',
            'is_admin': 'ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT 0',
            'is_banned': 'ALTER TABLE user ADD COLUMN is_banned BOOLEAN DEFAULT 0',
            'referral_code': 'ALTER TABLE user ADD COLUMN referral_code VARCHAR(20)',
            'referred_by': 'ALTER TABLE user ADD COLUMN referred_by VARCHAR(20)'
        }
        
        # Add missing columns
        for column_name, sql_command in required_columns.items():
            if column_name not in existing_columns:
                try:
                    cursor.execute(sql_command)
                    print(f"✅ Added column: {column_name}")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e).lower():
                        print(f"⚠️ Column {column_name} already exists")
                    else:
                        print(f"❌ Error adding column {column_name}: {e}")
            else:
                print(f"✅ Column {column_name} already exists")
        
        # Update NULL last_activity values to current time
        cursor.execute('UPDATE user SET last_activity = ? WHERE last_activity IS NULL', (datetime.utcnow(),))
        updated_rows = cursor.rowcount
        if updated_rows > 0:
            print(f"✅ Updated {updated_rows} NULL last_activity values")
        
        # Check and fix order table
        cursor.execute('PRAGMA table_info("order")')
        order_columns = [row[1] for row in cursor.fetchall()]
        print(f"📋 Current order table columns: {order_columns}")
        
        order_required_columns = {
            'start_count': 'ALTER TABLE "order" ADD COLUMN start_count INTEGER DEFAULT 0',
            'remains': 'ALTER TABLE "order" ADD COLUMN remains INTEGER DEFAULT 0',
            'completion_time': 'ALTER TABLE "order" ADD COLUMN completion_time VARCHAR(50)',
            'last_status_update': 'ALTER TABLE "order" ADD COLUMN last_status_update DATETIME'
        }
        
        for column_name, sql_command in order_required_columns.items():
            if column_name not in order_columns:
                try:
                    cursor.execute(sql_command)
                    print(f"✅ Added order column: {column_name}")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e).lower():
                        print(f"⚠️ Order column {column_name} already exists")
                    else:
                        print(f"❌ Error adding order column {column_name}: {e}")
            else:
                print(f"✅ Order column {column_name} already exists")
        
        # Update NULL last_status_update values
        cursor.execute('UPDATE "order" SET last_status_update = created_at WHERE last_status_update IS NULL')
        updated_order_rows = cursor.rowcount
        if updated_order_rows > 0:
            print(f"✅ Updated {updated_order_rows} NULL last_status_update values")
        
        # Commit all changes
        conn.commit()
        print("🎉 Database repair completed successfully!")
        
        # Verify the fixes
        cursor.execute('PRAGMA table_info(user)')
        final_user_columns = [row[1] for row in cursor.fetchall()]
        print(f"✅ Final user table columns: {final_user_columns}")
        
        cursor.execute('PRAGMA table_info("order")')
        final_order_columns = [row[1] for row in cursor.fetchall()]
        print(f"✅ Final order table columns: {final_order_columns}")
        
    except Exception as e:
        print(f"❌ Critical error during database repair: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    fix_database()
