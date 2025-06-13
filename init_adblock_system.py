
from main import app, db, AdBlockViolation

def init_adblock_system():
    """Initialize AdBlock violation tracking system"""
    with app.app_context():
        try:
            # Create all tables including the new AdBlockViolation table
            db.create_all()
            print("✅ AdBlockViolation table created successfully!")
            
            # Test the table
            test_count = AdBlockViolation.query.count()
            print(f"✅ AdBlock violations table working - Current count: {test_count}")
            
            print("✅ AdBlock violation tracking system initialized!")
            
        except Exception as e:
            print(f"❌ Error initializing AdBlock system: {e}")

if __name__ == "__main__":
    init_adblock_system()
