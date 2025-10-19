"""
Setup script to help configure the backend environment.
Run this script to create your .env file interactively.
"""
import os
import sys


def create_env_file():
    """Interactive script to create .env file."""
    print("=" * 60)
    print("🚀 Project Management API - Setup")
    print("=" * 60)
    print()
    
    # Check if .env already exists
    if os.path.exists(".env"):
        response = input("⚠️  .env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("❌ Setup cancelled. Existing .env file kept.")
            return
    
    print("📝 Please enter your Supabase credentials:")
    print("   (You can find these in your Supabase dashboard at Settings > API)")
    print()
    
    # Get Supabase credentials
    supabase_url = input("Supabase URL (e.g., https://xxx.supabase.co): ").strip()
    if not supabase_url:
        supabase_url = "https://your-project-id.supabase.co"
    
    supabase_key = input("Supabase Anon/Public Key: ").strip()
    if not supabase_key:
        supabase_key = "your_supabase_anon_key_here"
    
    supabase_service_key = input("Supabase Service Role Key (optional, press Enter to skip): ").strip()
    if not supabase_service_key:
        supabase_service_key = "your_supabase_service_role_key_here"
    
    print()
    print("⚙️  Server Configuration (press Enter for defaults):")
    
    app_host = input("Host [0.0.0.0]: ").strip() or "0.0.0.0"
    app_port = input("Port [8000]: ").strip() or "8000"
    
    # Create .env content
    env_content = f"""# Supabase Configuration
SUPABASE_URL={supabase_url}
SUPABASE_KEY={supabase_key}
SUPABASE_SERVICE_ROLE_KEY={supabase_service_key}

# Application Configuration
APP_HOST={app_host}
APP_PORT={app_port}
"""
    
    # Write .env file
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        print()
        print("=" * 60)
        print("✅ .env file created successfully!")
        print("=" * 60)
        print()
        print("📋 Next steps:")
        print("   1. Verify your Supabase credentials in .env")
        print("   2. Set up database tables (see SUPABASE_SCHEMA.md)")
        print("   3. Run the server: python run.py")
        print("   4. Visit http://localhost:8000/docs")
        print()
        print("💡 Tip: Check QUICKSTART.md for a quick guide!")
        print()
    except Exception as e:
        print()
        print(f"❌ Error creating .env file: {e}")
        print("   Please create it manually using env_template.txt")
        sys.exit(1)


def main():
    """Main setup function."""
    # Check if we're in the backend directory
    if not os.path.exists("run.py") or not os.path.exists("app"):
        print("❌ Error: Please run this script from the backend directory")
        print("   cd backend")
        print("   python setup.py")
        sys.exit(1)
    
    create_env_file()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user.")
        sys.exit(1)

