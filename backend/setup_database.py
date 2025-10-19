"""
Database setup script to create tables in Supabase.
Run this script to set up the database tables for the project management app.
"""
import os
from utils.config import get_supabase_client


def setup_database():
    """Set up the database tables."""
    try:
        supabase = get_supabase_client()
        
        print("Setting up database tables...")
        
        # Read the SQL file
        with open('sql/create_tables.sql', 'r') as f:
            sql_content = f.read()
        
        # Split into individual statements
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        # Execute each statement
        for i, statement in enumerate(statements):
            if statement and not statement.startswith('--'):
                try:
                    print(f"Executing statement {i+1}/{len(statements)}...")
                    result = supabase.rpc('exec_sql', {'sql': statement}).execute()
                    print(f"✅ Statement {i+1} executed successfully")
                except Exception as e:
                    print(f"❌ Error executing statement {i+1}: {e}")
                    print(f"Statement: {statement[:100]}...")
        
        print("\n🎉 Database setup completed!")
        print("You can now sign up and sign in with persistent user data.")
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        print("\nPlease make sure:")
        print("1. Your Supabase credentials are correct in .env file")
        print("2. Your Supabase project is active")
        print("3. You have the necessary permissions")


if __name__ == "__main__":
    setup_database()
