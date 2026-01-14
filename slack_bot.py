"""Slack Bolt app initialization and event handlers."""
import logging
from slack_bolt import App
import config

logger = logging.getLogger(__name__)

# Initialize Slack app (lazy initialization)
_app = None

def get_app():
    """Get or create Slack app."""
    global _app
    if _app is None:
        config.validate_config()
        _app = App(token=config.SLACK_BOT_TOKEN)
    return _app

# For backward compatibility
app = None  # Will be initialized on first use


def handle_mention(event, say):
    """Handle @mentions of the bot."""
    text = event.get('text', '').lower()
    
    if 'help' in text or 'commands' in text:
        say("Available commands:\n"
            "• `help` - Show this help message\n"
            "• `status` - Show bot status\n"
            "• `pending` - Show articles pending review")
    elif 'status' in text:
        from database import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        
        # Count pending reviews
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM articles a
            INNER JOIN classifications c ON a.id = c.article_id
            LEFT JOIN threat_assessments t ON a.id = t.article_id
            WHERE t.id IS NULL
        """)
        pending = cursor.fetchone()['count']
        
        # Count reviewed today
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM threat_assessments
            WHERE date(reviewed_at) = date('now')
        """)
        reviewed_today = cursor.fetchone()['count']
        
        conn.close()
        
        say(f"🤖 CI Bot Status:\n"
            f"• Articles pending review: {pending}\n"
            f"• Reviewed today: {reviewed_today}")
    elif 'pending' in text:
        from database import get_pending_reviews
        pending = get_pending_reviews()
        
        if pending:
            say(f"Found {len(pending)} articles pending review. "
                f"Run `python review_interface.py` to review them.")
        else:
            say("No articles pending review. ✓")
    else:
        say("Hi! I'm the CI Bot. Use `help` to see available commands.")


def handle_message(event, say):
    """Handle direct messages to the bot."""
    # Only respond to DMs, not channel messages
    if event.get('channel_type') == 'im':
        handle_mention(event, say)


def start_slack_app():
    """Start the Slack app (for future webhook/socket mode implementation)."""
    config.validate_config()
    app = get_app()
    app.event("app_mention")(handle_mention)
    app.event("message")(handle_message)
    logger.info("Slack bot initialized. Use slack_delivery for sending messages.")
    # For MVP, we use WebClient directly in slack_delivery.py
    # Future: implement socket mode or webhook handlers here

