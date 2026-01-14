"""Relevance filtering and classification orchestration."""
import logging
from typing import List, Dict
from database import get_connection, insert_classification
from llm_processor import classify_article, batch_classify_articles
import config

logger = logging.getLogger(__name__)


def filter_by_relevance(articles: List[Dict], threshold: int = None) -> List[Dict]:
    """Filter articles by relevance score.
    
    Args:
        articles: List of article dictionaries
        threshold: Minimum relevance score (defaults to config.RELEVANCE_THRESHOLD)
        
    Returns:
        Filtered list of articles meeting relevance threshold
    """
    if threshold is None:
        threshold = config.RELEVANCE_THRESHOLD
    
    relevant_articles = []
    for article in articles:
        # Articles need to be classified first
        # This function is mainly for filtering already-classified articles
        if 'relevance_score' in article:
            if article['relevance_score'] >= threshold:
                relevant_articles.append(article)
    
    return relevant_articles


def classify_and_store_articles(article_ids: List[int]) -> Dict[int, Dict]:
    """Classify articles and store results in database.
    
    Args:
        article_ids: List of article IDs to classify
        
    Returns:
        Dictionary mapping article_id to classification results
    """
    # Fetch articles from database
    conn = get_connection()
    cursor = conn.cursor()
    
    articles = []
    for article_id in article_ids:
        cursor.execute("""
            SELECT id, headline, full_text, url, source
            FROM articles
            WHERE id = ?
        """, (article_id,))
        row = cursor.fetchone()
        if row:
            articles.append(dict(row))
    
    conn.close()
    
    if not articles:
        logger.warning("No articles found to classify")
        return {}
    
    # Classify articles
    classifications = batch_classify_articles(articles)
    
    # Store classifications in database
    stored_count = 0
    for article_id, classification in classifications.items():
        try:
            insert_classification(
                article_id=article_id,
                relevance_score=classification['relevance'],
                category=classification['category'],
                product_impact=classification['product_impact'],
                summary=classification['summary'],
                llm_response=classification.get('llm_response', '')
            )
            stored_count += 1
        except Exception as e:
            logger.error(f"Error storing classification for article {article_id}: {e}")
    
    logger.info(f"Stored {stored_count} classifications")
    
    # Filter by relevance threshold
    relevant_classifications = {
        aid: cls for aid, cls in classifications.items()
        if cls['relevance'] >= config.RELEVANCE_THRESHOLD
    }
    
    logger.info(f"{len(relevant_classifications)}/{len(classifications)} articles meet relevance threshold")
    
    return relevant_classifications


def get_unclassified_articles(limit: int = 50) -> List[int]:
    """Get article IDs that haven't been classified yet."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.id
        FROM articles a
        LEFT JOIN classifications c ON a.id = c.article_id
        WHERE c.id IS NULL
        ORDER BY a.processed_at DESC
        LIMIT ?
    """, (limit,))
    article_ids = [row['id'] for row in cursor.fetchall()]
    conn.close()
    return article_ids

