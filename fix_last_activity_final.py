
from main import app, db, User
from datetime import datetime
from sqlalchemy import text

def fix_last_activity_column():
    """Fix the last_activity column in the user table"""
    with app.app_context():
        try:
            # Check if column exists first
            with db.engine.connect() as connection:
                # Check if column exists
                result = connection.execute(text("PRAGMA table_info(user)"))
                columns = [row[1] for row in result]
                
                if 'last_activity' not in columns:
                    print("Adding last_activity column...")
                    
                    # Create backup table
                    connection.execute(text('DROP TABLE IF EXISTS user_backup'))
                    connection.execute(text('''
                        CREATE TABLE user_backup AS 
                        SELECT id, username, email, password, coins, last_login_date, 
                               is_admin, is_banned, referral_code, referred_by 
                        FROM user
                    '''))
                    
                    # Drop original table
                    connection.execute(text('DROP TABLE user'))
                    
                    # Create new table with last_activity column
                    connection.execute(text('''
                        CREATE TABLE user (
                            id INTEGER PRIMARY KEY,
                            username VARCHAR(150) NOT NULL UNIQUE,
                            email VARCHAR(150) NOT NULL UNIQUE,
                            password VARCHAR(200) NOT NULL,
                            coins INTEGER DEFAULT 10,
                            last_login_date VARCHAR(20),
                            last_activity DATETIME,
                            is_admin BOOLEAN DEFAULT 0,
                            is_banned BOOLEAN DEFAULT 0,
                            referral_code VARCHAR(20) UNIQUE,
                            referred_by VARCHAR(20)
                        )
                    '''))
                    
                    # Restore data with default last_activity
                    connection.execute(text('''
                        INSERT INTO user (id, username, email, password, coins, last_login_date, 
                                        last_activity, is_admin, is_banned, referral_code, referred_by)
                        SELECT id, username, email, password, coins, last_login_date, 
                               datetime('now'), is_admin, is_banned, referral_code, referred_by
                        FROM user_backup
                    '''))
                    
                    # Drop backup table
                    connection.execute(text('DROP TABLE user_backup'))
                    
                    # Commit the transaction
                    connection.commit()
                    
                    print("✅ Successfully fixed last_activity column in user table")
                else:
                    print("✅ last_activity column already exists")
            
        except Exception as e:
            print(f"❌ Error fixing last_activity column: {e}")

if __name__ == "__main__":
    fix_last_activity_column()
