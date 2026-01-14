"""Configuration management for CI Bot."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

# Slack Channels
SLACK_CHANNEL_LEADERSHIP = os.getenv("SLACK_CHANNEL_LEADERSHIP", "product-competitor-intel-slt")
SLACK_CHANNEL_ALERTS = os.getenv("SLACK_CHANNEL_ALERTS", "competitor-intel-alerts")

# Processing Configuration
RELEVANCE_THRESHOLD = int(os.getenv("RELEVANCE_THRESHOLD", "3"))
MAX_DAILY_ITEMS = int(os.getenv("MAX_DAILY_ITEMS", "5"))
TIMEZONE = os.getenv("TIMEZONE", "America/New_York")

# Database Configuration
DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "data" / "ci_bot.db"))

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", str(BASE_DIR / "logs" / "ci_bot.log"))

# RSS Feed Sources
RSS_SOURCES = {
    "adexchanger": "https://www.adexchanger.com/feed/",
    "digiday": "https://digiday.com/feed/",
    "adage": "https://adage.com/rss",
    "adweek": "https://www.adweek.com/category/artificial-intelligence/feed/",
}

# Scheduled Times (24-hour format)
SCHEDULE_RSS_PROCESSING = "06:00"  # 6:00 AM daily
SCHEDULE_EDITOR_REMINDER = "07:30"  # 7:30 AM daily
SCHEDULE_DAILY_DIGEST = "08:00"  # 8:00 AM daily (Mon-Fri)
SCHEDULE_WEEKLY_SUMMARY = "16:00"  # 4:00 PM Friday

# Validation (only raise errors when actually using the config, not on import)
def validate_config():
    """Validate that required configuration is present."""
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY environment variable is required")
    if not SLACK_BOT_TOKEN:
        raise ValueError("SLACK_BOT_TOKEN environment variable is required")

