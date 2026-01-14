"""Threat level assignment logic."""
import logging
from typing import Optional
from database import insert_threat_assessment

logger = logging.getLogger(__name__)

# Valid threat levels
THREAT_LEVELS = ['HIGH', 'MEDIUM', 'LOW', 'OPPORTUNITY']

# Valid action recommendations
ACTION_RECOMMENDATIONS = ['Watch', 'Discuss', 'Urgent Response']

# Valid product impacts
PRODUCT_IMPACTS = ['AMP', 'Zero-Day', 'Both', 'General']


def validate_threat_level(threat_level: str) -> bool:
    """Validate threat level value."""
    return threat_level.upper() in THREAT_LEVELS


def validate_action_recommendation(action: str) -> bool:
    """Validate action recommendation value."""
    return action in ACTION_RECOMMENDATIONS


def validate_product_impact(product_impact: str) -> bool:
    """Validate product impact value."""
    return product_impact in PRODUCT_IMPACTS


def assign_threat_level(article_id: int, threat_level: str, product_impact: str,
                       action_recommendation: str, reviewed_by: str = "editor") -> bool:
    """Assign threat level and action recommendation to an article.
    
    Args:
        article_id: ID of the article
        threat_level: HIGH, MEDIUM, LOW, or OPPORTUNITY
        product_impact: AMP, Zero-Day, Both, or General
        action_recommendation: Watch, Discuss, or Urgent Response
        reviewed_by: Name/ID of the reviewer
        
    Returns:
        True if successful, False otherwise
    """
    # Validate inputs
    threat_level = threat_level.upper()
    if not validate_threat_level(threat_level):
        logger.error(f"Invalid threat level: {threat_level}")
        return False
    
    if not validate_action_recommendation(action_recommendation):
        logger.error(f"Invalid action recommendation: {action_recommendation}")
        return False
    
    if not validate_product_impact(product_impact):
        logger.error(f"Invalid product impact: {product_impact}")
        return False
    
    try:
        insert_threat_assessment(
            article_id=article_id,
            threat_level=threat_level,
            product_impact=product_impact,
            action_recommendation=action_recommendation,
            reviewed_by=reviewed_by
        )
        logger.info(f"Assigned threat level {threat_level} to article {article_id}")
        return True
    except Exception as e:
        logger.error(f"Error assigning threat level: {e}")
        return False


def update_action_recommendation(article_id: int, action_recommendation: str,
                              reviewed_by: str = "editor") -> bool:
    """Update action recommendation for an existing threat assessment."""
    if not validate_action_recommendation(action_recommendation):
        logger.error(f"Invalid action recommendation: {action_recommendation}")
        return False
    
    # Get existing assessment
    from database import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT threat_level, product_impact
        FROM threat_assessments
        WHERE article_id = ?
    """, (article_id,))
    existing = cursor.fetchone()
    conn.close()
    
    if not existing:
        logger.error(f"No threat assessment found for article {article_id}")
        return False
    
    return assign_threat_level(
        article_id=article_id,
        threat_level=existing['threat_level'],
        product_impact=existing['product_impact'],
        action_recommendation=action_recommendation,
        reviewed_by=reviewed_by
    )

