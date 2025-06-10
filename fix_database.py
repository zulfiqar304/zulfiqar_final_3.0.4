
import sqlite3
import os
from main import app

def migrate_database():
    """Migrate the database to add missing columns"""
    with app.app_context():
        try:
            print("Starting database migration...")
            
            # Get database path
            db_path = 'instance/users.db'
            
            # Create connection
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check which columns exist
            cursor.execute('PRAGMA table_info("order")')
            existing_columns = [row[1] for row in cursor.fetchall()]
            print(f"Existing columns: {existing_columns}")
            
            # Define columns to add
            columns_to_add = {
                'service_id': 'ALTER TABLE "order" ADD COLUMN service_id INTEGER',
                'service_name': 'ALTER TABLE "order" ADD COLUMN service_name VARCHAR(100)',
                'jap_order_id': 'ALTER TABLE "order" ADD COLUMN jap_order_id INTEGER',
                'coins_required': 'ALTER TABLE "order" ADD COLUMN coins_required INTEGER DEFAULT 0'
            }
            
            # Add missing columns
            for column_name, sql_command in columns_to_add.items():
                if column_name not in existing_columns:
                    try:
                        cursor.execute(sql_command)
                        print(f"Added column: {column_name}")
                    except sqlite3.OperationalError as e:
                        if "duplicate column name" in str(e).lower():
                            print(f"Column {column_name} already exists")
                        else:
                            print(f"Error adding column {column_name}: {e}")
                else:
                    print(f"Column {column_name} already exists")
            
            # Commit changes
            conn.commit()
            print("Database migration completed successfully!")
            
            # Verify the changes
            cursor.execute('PRAGMA table_info("order")')
            final_columns = [row[1] for row in cursor.fetchall()]
            print(f"Final columns: {final_columns}")
            
        except Exception as e:
            print(f"Migration error: {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    migrate_database()
