"""Setup script to initialize CI Bot."""
import sys
from pathlib import Path
from database import init_database

def main():
    """Initialize the CI Bot setup."""
    print("CI Bot MVP - Setup")
    print("="*80)
    
    # Check if .env exists
    env_file = Path(".env")
    if not env_file.exists():
        print("\n⚠️  Warning: .env file not found!")
        print("Please create a .env file based on .env.example")
        print("Required variables:")
        print("  - ANTHROPIC_API_KEY")
        print("  - SLACK_BOT_TOKEN")
        print("  - SLACK_CHANNEL_LEADERSHIP")
        print("  - SLACK_CHANNEL_ALERTS")
        response = input("\nContinue with database setup anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    else:
        print("✓ .env file found")
    
    # Initialize database
    print("\nInitializing database...")
    try:
        init_database()
        print("✓ Database initialized successfully")
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        sys.exit(1)
    
    # Create directories
    print("\nCreating directories...")
    directories = ['data', 'logs', 'tests']
    for dir_name in directories:
        dir_path = Path(dir_name)
        dir_path.mkdir(exist_ok=True)
        print(f"✓ {dir_name}/ directory ready")
    
    print("\n" + "="*80)
    print("Setup complete!")
    print("\nNext steps:")
    print("1. Ensure .env file is configured with API keys")
    print("2. Test the setup: python run_daily_pipeline.py")
    print("3. Review articles: python review_interface.py")
    print("4. Start scheduler: python main.py")
    print("="*80)

if __name__ == "__main__":
    main()

