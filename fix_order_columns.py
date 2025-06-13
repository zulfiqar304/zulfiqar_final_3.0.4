
from main import app, db
from sqlalchemy import text

def fix_order_columns():
    """Add missing columns to the Order table"""
    with app.app_context():
        try:
            # Get database inspector to check existing columns
            inspector = db.inspect(db.engine)
            order_columns = [col['name'] for col in inspector.get_columns('order')]
            print(f"Current order table columns: {order_columns}")
            
            # Define columns that should exist
            columns_to_add = {
                'start_count': 'ALTER TABLE "order" ADD COLUMN start_count INTEGER DEFAULT 0',
                'remains': 'ALTER TABLE "order" ADD COLUMN remains INTEGER DEFAULT 0', 
                'completion_time': 'ALTER TABLE "order" ADD COLUMN completion_time VARCHAR(50)',
                'last_status_update': 'ALTER TABLE "order" ADD COLUMN last_status_update DATETIME'
            }
            
            # Add missing columns
            with db.engine.connect() as connection:
                for column_name, sql_command in columns_to_add.items():
                    if column_name not in order_columns:
                        try:
                            connection.execute(text(sql_command))
                            print(f"✅ Added column: {column_name}")
                        except Exception as e:
                            print(f"❌ Error adding column {column_name}: {e}")
                    else:
                        print(f"⚠️ Column {column_name} already exists")
                
                connection.commit()
            
            print("✅ Order table migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during migration: {e}")
            db.session.rollback()

if __name__ == "__main__":
    fix_order_columns()
