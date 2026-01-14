"""Daily processing pipeline workflow."""
import logging
from datetime import datetime
from rss_aggregator import fetch_rss_feeds, store_articles
from classifier import classify_and_store_articles, get_unclassified_articles
from slack_delivery import send_high_priority_alert
from database import get_connection
from auto_reviewer import auto_review_pending_articles

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ci_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_daily_pipeline():
    """Execute the daily processing pipeline.
    
    Workflow:
    1. Fetch RSS feeds (last 24 hours)
    2. Deduplicate against existing articles
    3. Classify new articles with LLM
    4. Store classifications
    5. Flag for editor review
    6. Send high-priority alerts immediately
    """
    logger.info("="*80)
    logger.info("Starting daily pipeline")
    logger.info("="*80)
    
    try:
        # Step 1: Fetch RSS feeds
        logger.info("Step 1: Fetching RSS feeds...")
        articles = fetch_rss_feeds(hours_back=24)
        logger.info(f"Fetched {len(articles)} articles from RSS feeds")
        
        if not articles:
            logger.info("No new articles found. Pipeline complete.")
            return
        
        # Step 2: Store articles (with deduplication)
        logger.info("Step 2: Storing articles...")
        article_ids = store_articles(articles)
        logger.info(f"Stored {len(article_ids)} new articles")
        
        if not article_ids:
            logger.info("No new articles to process. Pipeline complete.")
            return
        
        # Step 3: Classify articles with LLM
        logger.info("Step 3: Classifying articles with LLM...")
        classifications = classify_and_store_articles(article_ids)
        logger.info(f"Classified {len(classifications)} articles")
        
        # Step 4: Auto-review classified articles with AI
        logger.info("Step 4: Auto-reviewing articles with AI...")
        review_results = auto_review_pending_articles()
        logger.info(f"Auto-reviewed {review_results['reviewed']}/{review_results['total']} articles")

        # Step 5: Check for high-priority items and send alerts
        logger.info("Step 5: Checking for high-priority items...")
        conn = get_connection()
        cursor = conn.cursor()

        # Get recently reviewed articles with high threat levels
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM threat_assessments
            WHERE threat_level IN ('HIGH', 'URGENT')
            AND datetime(reviewed_at) > datetime('now', '-1 hour')
        """)
        high_priority_count = cursor.fetchone()['count']

        if high_priority_count:
            logger.info(f"Found {high_priority_count} high-priority articles")

        conn.close()

        # Step 6: Summary
        logger.info("="*80)
        logger.info("Daily pipeline complete")
        logger.info(f"  Articles fetched: {len(articles)}")
        logger.info(f"  Articles stored: {len(article_ids)}")
        logger.info(f"  Articles classified: {len(classifications)}")
        logger.info(f"  Articles auto-reviewed: {review_results['reviewed']}")
        logger.info(f"  High priority: {high_priority_count}")
        logger.info("="*80)

        logger.info("Next steps:")
        logger.info("  1. Articles are ready for Slack delivery")
        logger.info("  2. Daily digest will be sent at 8:00 AM via scheduler")
        
    except Exception as e:
        logger.error(f"Error in daily pipeline: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    run_daily_pipeline()

