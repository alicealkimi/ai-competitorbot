"""Task scheduling using APScheduler."""
import logging
from datetime import datetime, time
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
import config
from run_daily_pipeline import run_daily_pipeline
from slack_delivery import send_daily_digest, send_weekly_summary
from database import get_pending_reviews

logger = logging.getLogger(__name__)

# Initialize scheduler
scheduler = BlockingScheduler(timezone=pytz.timezone(config.TIMEZONE))


def job_rss_processing():
    """Scheduled job: RSS aggregation and classification (6:00 AM daily)."""
    logger.info("Running scheduled RSS processing job...")
    try:
        run_daily_pipeline()
    except Exception as e:
        logger.error(f"Error in RSS processing job: {e}", exc_info=True)


def job_editor_reminder():
    """Scheduled job: Editor review reminder (7:30 AM daily)."""
    logger.info("Running scheduled editor reminder job...")
    try:
        pending = get_pending_reviews()
        if pending:
            count = len(pending)
            logger.info(f"Editor reminder: {count} articles pending review")
            # In future, could send Slack DM to editor
        else:
            logger.info("Editor reminder: No articles pending review")
    except Exception as e:
        logger.error(f"Error in editor reminder job: {e}", exc_info=True)


def job_daily_digest():
    """Scheduled job: Send daily digest (8:00 AM Mon-Fri)."""
    logger.info("Running scheduled daily digest job...")
    try:
        # Check if it's a weekday
        today = datetime.now(pytz.timezone(config.TIMEZONE))
        if today.weekday() < 5:  # Monday = 0, Friday = 4
            success = send_daily_digest()
            if success:
                logger.info("Daily digest sent successfully")
            else:
                logger.warning("Daily digest failed to send")
        else:
            logger.info("Skipping daily digest (weekend)")
    except Exception as e:
        logger.error(f"Error in daily digest job: {e}", exc_info=True)


def job_weekly_summary():
    """Scheduled job: Send weekly summary (4:00 PM Friday)."""
    logger.info("Running scheduled weekly summary job...")
    try:
        today = datetime.now(pytz.timezone(config.TIMEZONE))
        if today.weekday() == 4:  # Friday
            success = send_weekly_summary()
            if success:
                logger.info("Weekly summary sent successfully")
            else:
                logger.warning("Weekly summary failed to send")
        else:
            logger.info("Skipping weekly summary (not Friday)")
    except Exception as e:
        logger.error(f"Error in weekly summary job: {e}", exc_info=True)


def setup_scheduler():
    """Set up all scheduled jobs."""
    # RSS Processing: 6:00 AM daily
    scheduler.add_job(
        job_rss_processing,
        trigger=CronTrigger(hour=6, minute=0),
        id='rss_processing',
        name='RSS Processing',
        replace_existing=True
    )
    
    # Editor Reminder: 7:30 AM daily
    scheduler.add_job(
        job_editor_reminder,
        trigger=CronTrigger(hour=7, minute=30),
        id='editor_reminder',
        name='Editor Reminder',
        replace_existing=True
    )
    
    # Daily Digest: 8:00 AM Mon-Fri
    scheduler.add_job(
        job_daily_digest,
        trigger=CronTrigger(hour=8, minute=0, day_of_week='mon-fri'),
        id='daily_digest',
        name='Daily Digest',
        replace_existing=True
    )
    
    # Weekly Summary: 4:00 PM Friday
    scheduler.add_job(
        job_weekly_summary,
        trigger=CronTrigger(hour=16, minute=0, day_of_week='fri'),
        id='weekly_summary',
        name='Weekly Summary',
        replace_existing=True
    )
    
    logger.info("Scheduler configured with 4 jobs:")
    logger.info("  - RSS Processing: 6:00 AM daily")
    logger.info("  - Editor Reminder: 7:30 AM daily")
    logger.info("  - Daily Digest: 8:00 AM Mon-Fri")
    logger.info("  - Weekly Summary: 4:00 PM Friday")


def start_scheduler():
    """Start the scheduler."""
    setup_scheduler()
    logger.info("Starting scheduler...")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/ci_bot.log'),
            logging.StreamHandler()
        ]
    )
    
    start_scheduler()

