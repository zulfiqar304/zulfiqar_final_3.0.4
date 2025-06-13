
import os
from urllib.parse import urlparse

class Config:
    # Environment detection
    IS_REPLIT = os.getenv('REPLIT_DB_URL') is not None
    IS_RENDER = os.getenv('RENDER') is not None
    IS_LOCAL = not IS_REPLIT and not IS_RENDER
    
    # Database configuration
    if IS_RENDER:
        # For Render deployment, use PostgreSQL
        DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///users.db')
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # For Replit or local, use SQLite
        SQLALCHEMY_DATABASE_URI = 'sqlite:///users.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_super_secret_key_here')
    
    # Supabase configuration (optional for analytics)
    SUPABASE_URL = os.getenv('SUPABASE_URL', '')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')
    ENABLE_SUPABASE = bool(SUPABASE_URL and SUPABASE_KEY)
    
    # Server configuration
    if IS_RENDER:
        HOST = '0.0.0.0'
        PORT = int(os.getenv('PORT', 10000))
    else:
        HOST = '0.0.0.0'
        PORT = 5000
    
    # Ad configuration
    ENABLE_PUSH_NOTIFICATIONS = not IS_RENDER  # Disable for Render if causing issues
    
    @staticmethod
    def get_database_uri():
        return Config.SQLALCHEMY_DATABASE_URI
