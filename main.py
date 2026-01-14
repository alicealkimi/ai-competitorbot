"""Main entry point for CI Bot."""
import logging
import sys
from pathlib import Path
from scheduler import start_scheduler
from database import init_database

# Set up logging
log_file = Path("logs/ci_bot.log")
log_file.parent.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    logger.info("="*80)
    logger.info("CI Bot MVP - Starting...")
    logger.info("="*80)
    
    # Initialize database if needed
    try:
        init_database()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)
    
    # Start scheduler
    try:
        logger.info("Starting scheduler...")
        start_scheduler()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

