from supabase import create_client, Client
import os

# Supabase configuration from environment variables (with fallback defaults)
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://supabase.com/dashboard/project/qwpghbpprmmhhlxjsllc')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF3cGdoYnBwcm1taGhseGpzbGxjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk1NzY3MjAsImV4cCI6MjA2NTE1MjcyMH0.IB9Kaudy_X9sXL9G5_liJIMbFRgX0bY_0H9pzHBN52Y')

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Test connection function
def test_supabase_connection():
    """Test Supabase connection"""
    try:
        result = supabase.table('user_activity').select('*').limit(1).execute()
        return True, "Supabase connection successful"
    except Exception as e:
        return False, f"Supabase connection failed: {str(e)}"
