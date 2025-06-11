
from main import app, db, User
import uuid

def add_referral_columns():
    """Add referral system to database"""
    with app.app_context():
        try:
            # Create all new tables
            db.create_all()
            
            # Add referral_code and referred_by columns to existing users
            from sqlalchemy import text
            
            # Check if columns exist before adding
            inspector = db.inspect(db.engine)
            user_columns = [col['name'] for col in inspector.get_columns('user')]
            
            if 'referral_code' not in user_columns:
                with db.engine.connect() as connection:
                    connection.execute(text('ALTER TABLE user ADD COLUMN referral_code VARCHAR(20)'))
                    connection.commit()
                print("referral_code column added")
            
            if 'referred_by' not in user_columns:
                with db.engine.connect() as connection:
                    connection.execute(text('ALTER TABLE user ADD COLUMN referred_by VARCHAR(20)'))
                    connection.commit()
                print("referred_by column added")
            
            # Generate referral codes for existing users
            users_without_codes = User.query.filter_by(referral_code=None).all()
            for user in users_without_codes:
                # Generate unique referral code
                import string
                import random
                
                prefix = user.username[:3].upper()
                suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
                referral_code = prefix + suffix
                
                # Ensure uniqueness
                while User.query.filter_by(referral_code=referral_code).first():
                    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
                    referral_code = prefix + suffix
                
                user.referral_code = referral_code
                
            db.session.commit()
            print(f"Generated referral codes for {len(users_without_codes)} users")
            
            print("✅ Referral system database migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during migration: {e}")
            db.session.rollback()

if __name__ == "__main__":
    add_referral_columns()
