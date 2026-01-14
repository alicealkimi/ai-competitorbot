"""Article deduplication using headline similarity matching."""
import logging
from typing import List, Dict, Tuple, Optional
from thefuzz import fuzz
from database import get_connection

logger = logging.getLogger(__name__)


def calculate_similarity(headline1: str, headline2: str) -> int:
    """Calculate similarity score between two headlines (0-100)."""
    return fuzz.ratio(headline1.lower(), headline2.lower())


def find_similar_headlines(new_headline: str, threshold: int = 85) -> List[Dict]:
    """Find existing headlines similar to the new one."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, headline, url FROM articles")
    existing_articles = cursor.fetchall()
    conn.close()
    
    similar = []
    for article in existing_articles:
        similarity = calculate_similarity(new_headline, article['headline'])
        if similarity >= threshold:
            similar.append({
                'id': article['id'],
                'headline': article['headline'],
                'url': article['url'],
                'similarity': similarity
            })
    
    return similar


def is_duplicate(headline: str, url: str, similarity_threshold: int = 85) -> Tuple[bool, Optional[Dict]]:
    """Check if article is a duplicate based on URL or headline similarity.
    
    Returns:
        Tuple of (is_duplicate, existing_article_info)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # First check by URL (exact match)
    cursor.execute("SELECT id, headline, url FROM articles WHERE url = ?", (url,))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        return True, dict(existing)
    
    # Then check by headline similarity
    cursor.execute("SELECT id, headline, url FROM articles")
    all_articles = cursor.fetchall()
    conn.close()
    
    for article in all_articles:
        similarity = calculate_similarity(headline, article['headline'])
        if similarity >= similarity_threshold:
            logger.info(f"Found duplicate by similarity ({similarity}%): '{headline}' vs '{article['headline']}'")
            return True, dict(article)
    
    return False, None

