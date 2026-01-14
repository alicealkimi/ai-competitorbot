"""RSS feed aggregation and article collection."""
import feedparser
import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import config
from database import insert_article, article_exists
from deduplication import is_duplicate

logger = logging.getLogger(__name__)


def extract_article_content(url: str) -> Optional[str]:
    """Extract full text from article URL using web scraping fallback."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Try to find main content area (common patterns)
        content_selectors = [
            'article',
            '.article-content',
            '.post-content',
            '.entry-content',
            'main',
            '.content'
        ]
        
        content = None
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content:
                break
        
        if not content:
            # Fallback to body
            content = soup.find('body')
        
        if content:
            text = content.get_text(separator=' ', strip=True)
            # Clean up excessive whitespace
            text = ' '.join(text.split())
            return text[:10000]  # Limit to 10k characters
        
        return None
    except Exception as e:
        logger.warning(f"Failed to extract content from {url}: {e}")
        return None


def parse_feed_entry(entry, source: str) -> Optional[Dict]:
    """Parse a single RSS feed entry into article dict."""
    try:
        headline = entry.get('title', '').strip()
        url = entry.get('link', '').strip()
        
        if not headline or not url:
            logger.warning(f"Missing headline or URL in feed entry from {source}")
            return None
        
        # Parse publication date
        pub_date = None
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            try:
                pub_date = datetime(*entry.published_parsed[:6]).isoformat()
            except:
                pass
        
        if not pub_date and hasattr(entry, 'published'):
            try:
                pub_date = entry.published
            except:
                pass
        
        # Get full text from entry or scrape
        full_text = None
        if hasattr(entry, 'content') and entry.content:
            # Try to get content from RSS entry
            if isinstance(entry.content, list) and len(entry.content) > 0:
                full_text = entry.content[0].get('value', '')
            elif isinstance(entry.content, str):
                full_text = entry.content
        
        if not full_text and hasattr(entry, 'summary'):
            full_text = entry.summary
        
        # If still no text, try scraping
        if not full_text or len(full_text) < 100:
            full_text = extract_article_content(url)
        
        return {
            'headline': headline,
            'url': url,
            'source': source,
            'pub_date': pub_date,
            'full_text': full_text
        }
    except Exception as e:
        logger.error(f"Error parsing feed entry from {source}: {e}")
        return None


def fetch_rss_feeds(hours_back: int = 24) -> List[Dict]:
    """Fetch and parse RSS feeds from all configured sources.
    
    Args:
        hours_back: Only fetch articles from the last N hours
        
    Returns:
        List of article dictionaries
    """
    all_articles = []
    cutoff_time = datetime.now() - timedelta(hours=hours_back)
    
    for source_name, feed_url in config.RSS_SOURCES.items():
        try:
            logger.info(f"Fetching feed from {source_name}: {feed_url}")
            feed = feedparser.parse(feed_url)
            
            if feed.bozo and feed.bozo_exception:
                logger.warning(f"Feed parse error for {source_name}: {feed.bozo_exception}")
                continue
            
            entries_processed = 0
            for entry in feed.entries:
                article = parse_feed_entry(entry, source_name)
                if not article:
                    continue
                
                # Check if article is within time window
                if article['pub_date']:
                    try:
                        article_time = datetime.fromisoformat(article['pub_date'].replace('Z', '+00:00'))
                        if article_time.replace(tzinfo=None) < cutoff_time:
                            continue
                    except:
                        # If date parsing fails, include the article anyway
                        pass
                
                # Check for duplicates
                is_dup, existing = is_duplicate(article['headline'], article['url'])
                if is_dup:
                    logger.debug(f"Skipping duplicate: {article['headline'][:50]}...")
                    continue
                
                all_articles.append(article)
                entries_processed += 1
            
            logger.info(f"Processed {entries_processed} new articles from {source_name}")
            
        except Exception as e:
            logger.error(f"Error fetching feed from {source_name}: {e}")
            continue
    
    logger.info(f"Total new articles collected: {len(all_articles)}")
    return all_articles


def store_articles(articles: List[Dict]) -> List[int]:
    """Store articles in database, skipping duplicates.
    
    Returns:
        List of article IDs that were successfully stored
    """
    stored_ids = []
    for article in articles:
        try:
            # Double-check for duplicates before inserting
            is_dup, existing = is_duplicate(article['headline'], article['url'])
            if is_dup:
                if existing:
                    stored_ids.append(existing['id'])
                continue
            
            article_id = insert_article(
                headline=article['headline'],
                url=article['url'],
                source=article['source'],
                pub_date=article.get('pub_date'),
                full_text=article.get('full_text')
            )
            if article_id:
                stored_ids.append(article_id)
        except Exception as e:
            logger.error(f"Error storing article {article.get('headline', 'unknown')}: {e}")
            continue
    
    return stored_ids

