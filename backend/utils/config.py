"""
Configuration module for environment variables and Supabase client initialization.
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from .env file
load_dotenv()

# Environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
APP_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("BACKEND_PORT", "8010"))

# CORS Configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "Missing required environment variables. "
        "Please ensure SUPABASE_URL and SUPABASE_KEY are set in your .env file."
    )

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Service role client for admin operations (use with caution)
supabase_admin: Client = None
if SUPABASE_SERVICE_ROLE_KEY:
    supabase_admin = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def get_supabase_client() -> Client:
    """
    Get the Supabase client instance.
    
    Returns:
        Client: Supabase client instance
    """
    return supabase

def get_supabase_admin_client() -> Client:
    """
    Get the Supabase admin client instance (with service role key).
    Use this only for operations that require elevated permissions.
    
    Returns:
        Client: Supabase admin client instance
    """
    if not supabase_admin:
        raise ValueError("Service role key not configured")
    return supabase_admin

