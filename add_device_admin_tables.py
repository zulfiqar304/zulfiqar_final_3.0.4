
from main import app, db, DeviceRegistration, AdminSpinGrant
from sqlalchemy import text

def add_device_admin_tables():
    """Add device tracking and admin spin tables"""
    with app.app_context():
        try:
            # Create all new tables
            db.create_all()
            
            print("✅ Device tracking and admin spin tables created successfully!")
            
        except Exception as e:
            print(f"❌ Error during migration: {e}")
            db.session.rollback()

if __name__ == "__main__":
    add_device_admin_tables()
