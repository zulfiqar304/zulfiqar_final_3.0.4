
from supabase_config import supabase
import json

def create_user_activity_table():
    """Create user_activity table in Supabase"""
    try:
        # SQL to create table
        sql_query = """
        CREATE TABLE IF NOT EXISTS user_activity (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            username VARCHAR(150) NOT NULL,
            email VARCHAR(150) NOT NULL,
            coins INTEGER DEFAULT 0,
            last_activity TIMESTAMP,
            ads_watched_today INTEGER DEFAULT 0,
            direct_ads_watched_today INTEGER DEFAULT 0,
            is_online BOOLEAN DEFAULT FALSE,
            sync_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create unique index on user_id
        CREATE UNIQUE INDEX IF NOT EXISTS idx_user_activity_user_id ON user_activity(user_id);
        
        -- Create index on sync_timestamp for performance
        CREATE INDEX IF NOT EXISTS idx_user_activity_sync_timestamp ON user_activity(sync_timestamp);
        """
        
        # Execute SQL using Supabase RPC
        result = supabase.rpc('execute_sql', {'sql': sql_query}).execute()
        print("✅ Supabase user_activity table created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating Supabase table: {e}")
        
        # Alternative method - try direct SQL execution
        try:
            # Create table using direct query if RPC doesn't work
            result = supabase.table('user_activity').select('*').limit(1).execute()
            print("✅ Supabase user_activity table already exists or was created!")
            return True
        except Exception as e2:
            print(f"❌ Table creation failed: {e2}")
            print("Please create the table manually in Supabase dashboard:")
            print(sql_query)
            return False

def test_supabase_connection():
    """Test Supabase connection and table access"""
    try:
        # Test connection by trying to query the table
        result = supabase.table('user_activity').select('*').limit(1).execute()
        print("✅ Supabase connection successful!")
        print(f"Table access working. Data: {result.data}")
        return True
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return False

def sync_all_users_to_supabase():
    """Sync all existing users to Supabase"""
    from main import app, User
    
    with app.app_context():
        try:
            users = User.query.all()
            success_count = 0
            
            for user in users:
                from main import sync_user_data_to_supabase
                if sync_user_data_to_supabase(user.id):
                    success_count += 1
                    print(f"✅ Synced user: {user.username}")
                else:
                    print(f"❌ Failed to sync user: {user.username}")
            
            print(f"✅ Successfully synced {success_count}/{len(users)} users to Supabase!")
            
        except Exception as e:
            print(f"❌ Error syncing users: {e}")

if __name__ == "__main__":
    print("🚀 Setting up Supabase integration...")
    
    # Test connection
    if test_supabase_connection():
        print("✅ Supabase connection verified!")
    else:
        print("❌ Please check your Supabase configuration!")
        exit(1)
    
    # Create table
    create_user_activity_table()
    
    # Sync all existing users
    print("\n📊 Syncing all existing users to Supabase...")
    sync_all_users_to_supabase()
    
    print("\n🎉 Supabase integration setup complete!")
    print("Your user data will now be automatically synced to Supabase database!")
