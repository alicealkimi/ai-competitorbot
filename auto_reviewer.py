"""Automated AI-powered review of classified articles."""
import logging
from typing import Dict, Optional
from database import get_pending_reviews
from threat_scorer import assign_threat_level
from llm_processor import get_client

logger = logging.getLogger(__name__)


def get_review_prompt(article: dict) -> str:
    """Generate prompt for AI review of an article."""
    return f"""You are reviewing a competitive intelligence article for a Web3 advertising company that operates two products:
1. AMP (Advertising Marketplace Platform)
2. Zero-Day (Ad reporting/analytics product)

Review this article and provide threat assessment:

ARTICLE DETAILS:
Headline: {article.get('headline', 'N/A')}
Source: {article.get('source', 'N/A')}
URL: {article.get('url', 'N/A')}
Published: {article.get('pub_date', 'N/A')}

AI CLASSIFICATION:
Relevance Score: {article.get('relevance_score', 'N/A')}/5
Category: {article.get('category', 'N/A')}
Product Impact: {article.get('product_impact', 'N/A')}
Summary: {article.get('summary', 'N/A')}

ARTICLE TEXT:
{article.get('full_text', article.get('summary', 'N/A'))[:2000]}

Based on this information, provide your assessment in JSON format:

{{
  "threat_level": "HIGH|MEDIUM|LOW|OPPORTUNITY",
  "product_impact": "AMP|Zero-Day|Both|General",
  "action_recommendation": "Watch|Discuss|Urgent Response",
  "reasoning": "Brief explanation of your assessment"
}}

Guidelines:
- HIGH: Direct competitive threat or major market shift
- MEDIUM: Relevant competitive activity worth monitoring
- LOW: Minor competitive news, tangentially relevant
- OPPORTUNITY: Potential partnership or market opportunity
- Watch: Monitor for updates
- Discuss: Bring to team discussion
- Urgent Response: Requires immediate action"""


def parse_review_response(response_text: str) -> Optional[Dict]:
    """Parse JSON review response from Claude."""
    import json

    try:
        # Remove markdown code blocks if present
        response_text = response_text.strip()
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1])
            if response_text.startswith("json"):
                response_text = response_text[4:].strip()

        data = json.loads(response_text)

        # Validate required fields
        required_fields = ['threat_level', 'product_impact', 'action_recommendation']
        if not all(field in data for field in required_fields):
            logger.warning(f"Missing required fields in review response: {data}")
            return None

        return data
    except Exception as e:
        logger.error(f"Error parsing review response: {e}")
        return None


def auto_review_article(article: dict) -> bool:
    """Automatically review an article using Claude AI.

    Args:
        article: Article dictionary with classification data

    Returns:
        True if successfully reviewed and stored, False otherwise
    """
    try:
        prompt = get_review_prompt(article)
        client = get_client()

        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        response_text = message.content[0].text if message.content else ""

        if not response_text:
            logger.warning(f"Empty response from Claude for article {article['id']}")
            return False

        # Parse the review
        review = parse_review_response(response_text)

        if not review:
            logger.warning(f"Failed to parse review for article {article['id']}")
            return False

        # Store the threat assessment
        success = assign_threat_level(
            article_id=article['id'],
            threat_level=review['threat_level'],
            product_impact=review['product_impact'],
            action_recommendation=review['action_recommendation'],
            reviewed_by="ai-auto-reviewer"
        )

        if success:
            logger.info(f"Auto-reviewed article {article['id']}: {review['threat_level']}, {review['action_recommendation']}")
            if 'reasoning' in review:
                logger.debug(f"Review reasoning: {review['reasoning']}")

        return success

    except Exception as e:
        logger.error(f"Error auto-reviewing article {article['id']}: {e}")
        return False


def auto_review_pending_articles() -> Dict[str, int]:
    """Automatically review all pending articles.

    Returns:
        Dictionary with counts: {'reviewed': n, 'failed': n, 'total': n}
    """
    pending = get_pending_reviews()

    if not pending:
        logger.info("No articles pending review")
        return {'reviewed': 0, 'failed': 0, 'total': 0}

    logger.info(f"Auto-reviewing {len(pending)} pending articles...")

    reviewed_count = 0
    failed_count = 0

    for article in pending:
        if auto_review_article(article):
            reviewed_count += 1
        else:
            failed_count += 1

    logger.info(f"Auto-review complete: {reviewed_count} reviewed, {failed_count} failed")

    return {
        'reviewed': reviewed_count,
        'failed': failed_count,
        'total': len(pending)
    }


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    results = auto_review_pending_articles()

    print(f"\nAuto-Review Results:")
    print(f"  Total articles: {results['total']}")
    print(f"  Successfully reviewed: {results['reviewed']}")
    print(f"  Failed: {results['failed']}")
