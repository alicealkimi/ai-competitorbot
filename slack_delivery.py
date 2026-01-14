"""Slack message delivery logic."""
import logging
from typing import List, Dict, Optional
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import config
from message_formatter import format_daily_digest, format_weekly_summary, format_high_priority_alert
from database import record_delivery, get_reviewed_articles_for_digest, get_weekly_stats
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Initialize Slack client (lazy initialization)
_client = None

def get_client():
    """Get or create Slack client."""
    global _client
    if _client is None:
        config.validate_config()
        _client = WebClient(token=config.SLACK_BOT_TOKEN)
    return _client


def send_to_channel(channel: str, blocks: List[Dict], text: str = None) -> Optional[str]:
    """Send message blocks to a Slack channel.
    
    Args:
        channel: Channel ID or name
        blocks: List of Slack Block Kit blocks
        text: Fallback text (required for notifications)
        
    Returns:
        Message timestamp (ts) if successful, None otherwise
    """
    try:
        client = get_client()
        response = client.chat_postMessage(
            channel=channel,
            blocks=blocks,
            text=text or "CI Bot Update"
        )
        
        if response["ok"]:
            message_ts = response["ts"]
            logger.info(f"Successfully sent message to {channel}")
            return message_ts
        else:
            logger.error(f"Slack API error: {response.get('error')}")
            return None
            
    except SlackApiError as e:
        logger.error(f"Slack API error: {e.response['error']}")
        return None
    except Exception as e:
        logger.error(f"Error sending message to Slack: {e}")
        return None


def send_daily_digest(channel: str = None, max_items: int = None) -> bool:
    """Send daily digest to Slack channel.
    
    Args:
        channel: Channel to send to (defaults to config.SLACK_CHANNEL_LEADERSHIP)
        max_items: Maximum number of items (defaults to config.MAX_DAILY_ITEMS)
        
    Returns:
        True if successful, False otherwise
    """
    if channel is None:
        channel = config.SLACK_CHANNEL_LEADERSHIP
    
    if max_items is None:
        max_items = config.MAX_DAILY_ITEMS
    
    # Get reviewed articles
    articles = get_reviewed_articles_for_digest(limit=max_items)
    
    if not articles:
        logger.info("No articles available for daily digest")
        return False
    
    # Format message
    blocks = format_daily_digest(articles)
    
    # Send message
    message_ts = send_to_channel(
        channel=channel,
        blocks=blocks,
        text=f"CI-Bot Daily Brief - {len(articles)} articles"
    )
    
    if message_ts:
        # Record delivery
        article_ids = [a['id'] for a in articles]
        record_delivery(
            delivery_type='daily_digest',
            delivery_date=datetime.now().isoformat(),
            channel=channel,
            message_id=message_ts,
            articles_included=article_ids
        )
        logger.info(f"Sent daily digest with {len(articles)} articles")
        return True
    
    return False


def send_weekly_summary(channel: str = None) -> bool:
    """Send weekly summary to Slack channel.
    
    Args:
        channel: Channel to send to (defaults to config.SLACK_CHANNEL_LEADERSHIP)
        
    Returns:
        True if successful, False otherwise
    """
    if channel is None:
        channel = config.SLACK_CHANNEL_LEADERSHIP
    
    # Calculate week range (Monday to Friday)
    today = datetime.now()
    # Get Monday of current week
    days_since_monday = today.weekday()
    monday = today - timedelta(days=days_since_monday)
    friday = monday + timedelta(days=4)
    
    start_date = monday.isoformat()
    end_date = friday.isoformat()
    
    # Get weekly stats
    stats = get_weekly_stats(start_date, end_date)
    
    # Format message
    blocks = format_weekly_summary(stats, start_date, end_date)
    
    # Send message
    message_ts = send_to_channel(
        channel=channel,
        blocks=blocks,
        text=f"CI-Bot Weekly Summary - {stats.get('total_scanned', 0)} articles scanned"
    )
    
    if message_ts:
        # Record delivery
        record_delivery(
            delivery_type='weekly_summary',
            delivery_date=datetime.now().isoformat(),
            channel=channel,
            message_id=message_ts,
            articles_included=[]
        )
        logger.info("Sent weekly summary")
        return True
    
    return False


def send_high_priority_alert(article: Dict, channel: str = None) -> bool:
    """Send immediate notification for HIGH priority threats.
    
    Args:
        article: Article dictionary with threat assessment
        channel: Channel to send to (defaults to config.SLACK_CHANNEL_ALERTS)
        
    Returns:
        True if successful, False otherwise
    """
    if channel is None:
        channel = config.SLACK_CHANNEL_ALERTS
    
    if article.get('threat_level') != 'HIGH':
        logger.warning(f"Article {article.get('id')} is not HIGH priority")
        return False
    
    # Format alert
    blocks = format_high_priority_alert(article)
    
    # Send with @channel mention for immediate attention
    alert_text = f"<!channel> HIGH PRIORITY ALERT: {article.get('headline', 'Unknown')}"
    
    message_ts = send_to_channel(
        channel=channel,
        blocks=blocks,
        text=alert_text
    )
    
    if message_ts:
        logger.info(f"Sent high priority alert for article {article.get('id')}")
        return True
    
    return False

