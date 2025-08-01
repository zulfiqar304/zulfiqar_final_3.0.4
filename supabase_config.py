
from supabase import create_client
import os

# Supabase configuration from environment variables
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://qwpghbpprmmhhlxjsllc.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF3cGdoYnBwcm1taGhseGpzbGxjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk1NzY3MjAsImV4cCI6MjA2NTE1MjcyMH0.IB9Kaudy_X9sXL9G5_liJIMbFRgX0bY_0H9pzHBN52Y')

# Create Supabase client with better error handling
try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"Failed to initialize Supabase client: {e}")
    supabase = None

# Test connection function
def test_supabase_connection():
    """Test Supabase connection"""
    try:
        # Try to access a simple endpoint
        result = supabase.table('user_activity').select('*').limit(1).execute()
        return True, "Supabase connection successful"
    except Exception as e:
        return False, f"Supabase connection failed: {str(e)}"

def get_supabase_stats():
    """Get statistics from Supabase"""
    try:
        # Get total users count
        result = supabase.table('user_activity').select('*', count='exact').execute()
        total_users = result.count
        
        # Get online users count
        online_result = supabase.table('user_activity').select('*').eq('is_online', True).execute()
        online_users = len(online_result.data)
        
        return {
            'total_users': total_users,
            'online_users': online_users,
            'last_sync': 'Connected'
        }
    except Exception as e:
        return {
            'total_users': 0,
            'online_users': 0,
            'last_sync': f'Error: {str(e)}'
        }
