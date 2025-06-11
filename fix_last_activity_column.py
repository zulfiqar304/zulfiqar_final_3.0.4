
from main import app, db, User
from datetime import datetime
from sqlalchemy import text

def fix_last_activity_column():
    """Add last_activity column to existing User table"""
    with app.app_context():
        try:
            # Check if column exists
            inspector = db.inspect(db.engine)
            user_columns = [col['name'] for col in inspector.get_columns('user')]
            
            if 'last_activity' not in user_columns:
                # Add the column
                with db.engine.connect() as connection:
                    connection.execute(text('ALTER TABLE user ADD COLUMN last_activity DATETIME DEFAULT CURRENT_TIMESTAMP'))
                    connection.commit()
                print("✅ last_activity column added successfully!")
                
                # Update all existing users with current timestamp
                users = User.query.all()
                for user in users:
                    user.last_activity = datetime.utcnow()
                
                db.session.commit()
                print(f"✅ Updated last_activity for {len(users)} existing users!")
            else:
                print("✅ last_activity column already exists!")
                
        except Exception as e:
            print(f"❌ Error adding last_activity column: {e}")
            db.session.rollback()

if __name__ == "__main__":
    fix_last_activity_column()
