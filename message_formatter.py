"""Slack message formatting for daily digests and weekly summaries."""
from datetime import datetime
from typing import List, Dict
import config


def get_threat_emoji(threat_level: str) -> str:
    """Get emoji for threat level."""
    emoji_map = {
        'HIGH': '🔴',
        'MEDIUM': '🟡',
        'LOW': '🟢',
        'OPPORTUNITY': '🔵'
    }
    return emoji_map.get(threat_level.upper(), '⚪')


def get_source_emoji(source: str) -> str:
    """Get emoji for source."""
    emoji_map = {
        'adexchanger': '📰',
        'digiday': '📰',
        'adage': '📰',
        'adweek': '📰'
    }
    return emoji_map.get(source.lower(), '📄')


def format_daily_digest(articles: List[Dict], date: datetime = None) -> List[Dict]:
    """Format daily digest message per PRD Section 5.2.
    
    Args:
        articles: List of article dictionaries with threat assessments
        date: Date for the digest (defaults to today)
        
    Returns:
        List of Slack Block Kit blocks
    """
    if date is None:
        date = datetime.now()
    
    date_str = date.strftime("%a, %b %d, %Y")
    
    blocks = []
    
    # Header
    blocks.append({
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": f"🤖 CI-Bot Daily Brief | {date_str}"
        }
    })
    
    blocks.append({"type": "divider"})
    
    # Articles
    for article in articles:
        threat_level = article.get('threat_level', 'LOW')
        emoji = get_threat_emoji(threat_level)
        source_emoji = get_source_emoji(article.get('source', ''))
        
        # Format product impact
        product_impact = article.get('product_impact', 'General')
        if product_impact == 'AMP':
            impact_text = "AMP Threat"
        elif product_impact == 'Zero-Day':
            impact_text = "Zero-Day Watch"
        elif product_impact == 'Both':
            impact_text = "AMP + Zero-Day"
        else:
            impact_text = "Market Validation"
        
        # Build article text
        headline = article.get('headline', 'No headline')
        summary = article.get('summary', 'No summary available')
        
        # Truncate if too long
        if len(summary) > 200:
            summary = summary[:197] + "..."
        
        article_text = f"{emoji} {threat_level} | {impact_text}\n"
        article_text += f"*{headline}*\n"
        article_text += f"{summary}\n"
        article_text += f"⚡ Action: {article.get('action_recommendation', 'Watch')} | {source_emoji} {article.get('source', 'Unknown')}"
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": article_text
            }
        })
        
        # Add URL button if available
        if article.get('url'):
            blocks.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Read Article"
                        },
                        "url": article['url']
                    }
                ]
            })
        
        blocks.append({"type": "divider"})
    
    # Footer with stats
    total_scanned = len(articles)  # This would come from pipeline stats
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"📊 Today: {total_scanned} articles scanned | {len(articles)} surfaced | {sum(1 for a in articles if a.get('threat_level') == 'HIGH')} high priority"
        }
    })
    
    return blocks


def format_weekly_summary(stats: Dict, start_date: str, end_date: str) -> List[Dict]:
    """Format weekly summary message per PRD Section 5.3.
    
    Args:
        stats: Statistics dictionary from get_weekly_stats
        start_date: Start date of the week (ISO format)
        end_date: End date of the week (ISO format)
        
    Returns:
        List of Slack Block Kit blocks
    """
    blocks = []
    
    # Parse dates for display
    try:
        start = datetime.fromisoformat(start_date.split('T')[0])
        end = datetime.fromisoformat(end_date.split('T')[0])
        date_range = f"{start.strftime('%b %d')} - {end.strftime('%b %d, %Y')}"
    except:
        date_range = f"{start_date} - {end_date}"
    
    # Header
    blocks.append({
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": f"📊 CI-Bot Weekly Summary | {date_range}"
        }
    })
    
    blocks.append({"type": "divider"})
    
    # Weekly volume
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*📈 WEEKLY VOLUME*\n"
                   f"Articles Scanned: {stats.get('total_scanned', 0)} | "
                   f"Relevant: {stats.get('relevant', 0)} | "
                   f"High Priority: {stats.get('high_priority', 0)}"
        }
    })
    
    blocks.append({"type": "divider"})
    
    # Threat summary
    threat_text = "*⚔️ THREAT SUMMARY*\n"
    product_breakdown = stats.get('product_breakdown', {})
    
    if 'AMP' in product_breakdown:
        threat_text += f"• AMP: {product_breakdown['AMP']} items"
        # Add competitor mentions if available
        threat_text += "\n"
    
    if 'Zero-Day' in product_breakdown:
        threat_text += f"• Zero-Day: {product_breakdown['Zero-Day']} items\n"
    
    if 'Both' in product_breakdown:
        threat_text += f"• Both: {product_breakdown['Both']} items\n"
    
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": threat_text
        }
    })
    
    blocks.append({"type": "divider"})
    
    # Key trend (placeholder - would need trend analysis)
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*🔥 KEY TREND:* *Agent-to-agent media buying* (3 mentions)\n\n"
                   "*💬 Suggested topic for Monday strategy sync*"
        }
    })
    
    return blocks


def format_high_priority_alert(article: Dict) -> List[Dict]:
    """Format high-priority alert for immediate notification.
    
    Args:
        article: Article dictionary with threat assessment
        
    Returns:
        List of Slack Block Kit blocks
    """
    blocks = []
    
    blocks.append({
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": "🚨 HIGH PRIORITY ALERT"
        }
    })
    
    blocks.append({"type": "divider"})
    
    headline = article.get('headline', 'No headline')
    summary = article.get('summary', 'No summary available')
    product_impact = article.get('product_impact', 'General')
    
    alert_text = f"*{headline}*\n\n"
    alert_text += f"{summary}\n\n"
    alert_text += f"*Product Impact:* {product_impact}\n"
    alert_text += f"*Action Required:* {article.get('action_recommendation', 'Urgent Response')}"
    
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": alert_text
        }
    })
    
    if article.get('url'):
        blocks.append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Read Article"
                    },
                    "url": article['url'],
                    "style": "danger"
                }
            ]
        })
    
    return blocks

