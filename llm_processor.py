"""Claude API integration for article classification."""
import json
import logging
import time
from typing import Dict, Optional
from anthropic import Anthropic
import config

logger = logging.getLogger(__name__)

# Initialize Claude client (lazy initialization)
_client = None

def get_client():
    """Get or create Claude client."""
    global _client
    if _client is None:
        config.validate_config()
        _client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
    return _client


def parse_llm_response(response_text: str) -> Optional[Dict]:
    """Parse JSON response from LLM, handling various formats."""
    try:
        # Try to extract JSON from response (may have markdown code blocks)
        response_text = response_text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            # Remove first and last line (code block markers)
            response_text = "\n".join(lines[1:-1])
            # Remove language identifier if present
            if response_text.startswith("json"):
                response_text = response_text[4:].strip()
        
        # Parse JSON
        data = json.loads(response_text)
        
        # Validate required fields
        required_fields = ['relevance', 'category', 'product_impact', 'summary']
        if not all(field in data for field in required_fields):
            logger.warning(f"Missing required fields in LLM response: {data}")
            return None
        
        # Ensure relevance is an integer between 1-5
        if isinstance(data['relevance'], str):
            try:
                data['relevance'] = int(data['relevance'])
            except:
                data['relevance'] = 3  # Default
        
        data['relevance'] = max(1, min(5, int(data['relevance'])))
        
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM JSON response: {e}")
        logger.debug(f"Response text: {response_text[:500]}")
        return None
    except Exception as e:
        logger.error(f"Error parsing LLM response: {e}")
        return None


def classify_article(article_text: str, headline: str, max_retries: int = 3) -> Optional[Dict]:
    """Classify an article using Claude API.
    
    Args:
        article_text: Full text of the article
        headline: Article headline for context
        max_retries: Maximum number of retry attempts
        
    Returns:
        Dictionary with classification results or None if failed
    """
    from prompts import get_classification_prompt
    
    # Prepare article text (prepend headline for context)
    full_text = f"Headline: {headline}\n\n{article_text}" if article_text else headline
    
    prompt = get_classification_prompt(full_text)
    
    for attempt in range(max_retries):
        try:
            logger.debug(f"Classifying article (attempt {attempt + 1}): {headline[:50]}...")
            
            client = get_client()
            message = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            response_text = message.content[0].text if message.content else ""
            
            if not response_text:
                logger.warning("Empty response from Claude API")
                continue
            
            # Parse the response
            classification = parse_llm_response(response_text)
            
            if classification:
                # Store raw response for debugging
                classification['llm_response'] = response_text
                logger.info(f"Successfully classified article: relevance={classification['relevance']}, category={classification['category']}")
                return classification
            else:
                logger.warning(f"Failed to parse classification response (attempt {attempt + 1})")
                
        except Exception as e:
            logger.error(f"Error calling Claude API (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                # Exponential backoff
                wait_time = 2 ** attempt
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                logger.error(f"Failed to classify article after {max_retries} attempts")
    
    return None


def batch_classify_articles(articles: list) -> Dict[int, Dict]:
    """Classify multiple articles with rate limiting.
    
    Args:
        articles: List of dicts with 'id', 'headline', 'full_text' keys
        
    Returns:
        Dictionary mapping article_id to classification results
    """
    results = {}
    
    for i, article in enumerate(articles):
        article_id = article.get('id')
        headline = article.get('headline', '')
        full_text = article.get('full_text', '') or article.get('summary', '')
        
        if not headline:
            logger.warning(f"Skipping article {article_id}: no headline")
            continue
        
        classification = classify_article(full_text, headline)
        
        if classification:
            results[article_id] = classification
        else:
            logger.warning(f"Failed to classify article {article_id}: {headline[:50]}")
        
        # Rate limiting: small delay between requests
        if i < len(articles) - 1:
            time.sleep(0.5)
    
    logger.info(f"Classified {len(results)}/{len(articles)} articles")
    return results

