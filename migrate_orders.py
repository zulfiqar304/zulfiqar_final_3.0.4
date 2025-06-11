
from main import db, app

def migrate_order_table():
    """Add new columns to existing Order table"""
    with app.app_context():
        try:
            # Add new columns
            db.engine.execute('ALTER TABLE "order" ADD COLUMN service_id INTEGER')
            db.engine.execute('ALTER TABLE "order" ADD COLUMN service_name VARCHAR(100)')
            db.engine.execute('ALTER TABLE "order" ADD COLUMN jap_order_id INTEGER')
            print("Successfully added new columns to Order table")
        except Exception as e:
            print(f"Migration may have already been applied or error occurred: {e}")
        
        # Update existing records
        try:
            db.engine.execute('UPDATE "order" SET service_name = service WHERE service_name IS NULL')
            print("Updated existing records with service names")
        except Exception as e:
            print(f"Error updating existing records: {e}")

if __name__ == "__main__":
    migrate_order_table()
