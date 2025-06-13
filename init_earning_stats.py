
from main import app, db, UserEarningStats, AdPerformanceStats

def init_earning_stats():
    """Initialize earning statistics tables"""
    with app.app_context():
        try:
            # Create tables
            db.create_all()
            print("✅ Earning statistics tables created successfully!")
            
            # Check if tables exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'user_earning_stats' in tables:
                print("✅ UserEarningStats table created")
            if 'ad_performance_stats' in tables:
                print("✅ AdPerformanceStats table created")
                
        except Exception as e:
            print(f"❌ Error creating tables: {e}")

if __name__ == "__main__":
    init_earning_stats()
