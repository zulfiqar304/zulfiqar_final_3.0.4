
from main import app, db
from sqlalchemy import text

def add_pagevisit_table():
    """Add page visit tracking table for referral validation"""
    with app.app_context():
        try:
            # Create the PageVisit table
            with db.engine.connect() as connection:
                connection.execute(text('''
                    CREATE TABLE IF NOT EXISTS page_visit (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        device_id VARCHAR(100) NOT NULL,
                        visit_start DATETIME DEFAULT CURRENT_TIMESTAMP,
                        visit_end DATETIME,
                        duration_seconds INTEGER DEFAULT 0,
                        is_qualified BOOLEAN DEFAULT FALSE,
                        ip_address VARCHAR(50),
                        user_agent VARCHAR(500),
                        referral_code VARCHAR(20),
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES user (id)
                    )
                '''))
                connection.commit()
            
            print("✅ PageVisit table created successfully!")
            
        except Exception as e:
            print(f"❌ Error during migration: {e}")
            db.session.rollback()

if __name__ == "__main__":
    add_pagevisit_table()
