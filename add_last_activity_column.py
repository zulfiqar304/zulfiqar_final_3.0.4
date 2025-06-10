
from main import app, db, User
from datetime import datetime

def add_last_activity_column():
    """Add last_activity column to existing User table"""
    with app.app_context():
        try:
            # Try to add the column if it doesn't exist
            db.engine.execute('ALTER TABLE user ADD COLUMN last_activity DATETIME')
            print("✅ last_activity column added successfully!")
            
            # Update all existing users with current timestamp
            users = User.query.all()
            for user in users:
                user.last_activity = datetime.utcnow()
            
            db.session.commit()
            print(f"✅ Updated last_activity for {len(users)} existing users!")
            
        except Exception as e:
            if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                print("✅ last_activity column already exists!")
            else:
                print(f"❌ Error adding last_activity column: {e}")

if __name__ == "__main__":
    add_last_activity_column()
