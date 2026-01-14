"""CLI interface for editor review of classified articles."""
import sys
import logging
from typing import Optional
from database import get_pending_reviews
from threat_scorer import assign_threat_level, THREAT_LEVELS, ACTION_RECOMMENDATIONS, PRODUCT_IMPACTS

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def display_article(article: dict):
    """Display article information for review."""
    print("\n" + "="*80)
    print(f"Article ID: {article['id']}")
    print(f"Headline: {article['headline']}")
    print(f"Source: {article['source']}")
    print(f"URL: {article['url']}")
    print(f"Published: {article.get('pub_date', 'Unknown')}")
    print("\nAI Classification:")
    print(f"  Relevance Score: {article.get('relevance_score', 'N/A')}/5")
    print(f"  Category: {article.get('category', 'N/A')}")
    print(f"  Product Impact: {article.get('product_impact', 'N/A')}")
    print(f"  Summary: {article.get('summary', 'N/A')}")
    print("="*80)


def get_user_input(prompt: str, valid_options: list = None, default: str = None) -> str:
    """Get user input with validation."""
    while True:
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            if not user_input:
                return default
        else:
            user_input = input(f"{prompt}: ").strip()
        
        if not valid_options:
            return user_input
        
        if user_input.upper() in [opt.upper() for opt in valid_options]:
            return user_input.upper() if user_input.upper() in [opt.upper() for opt in valid_options] else user_input
        
        print(f"Invalid input. Please choose from: {', '.join(valid_options)}")


def review_article(article: dict) -> bool:
    """Review a single article and assign threat level."""
    display_article(article)
    
    print("\nReview Options:")
    print("  Threat Levels:", ", ".join(THREAT_LEVELS))
    print("  Product Impact:", ", ".join(PRODUCT_IMPACTS))
    print("  Actions:", ", ".join(ACTION_RECOMMENDATIONS))
    print("\nEnter 'skip' to skip this article, 'quit' to exit")
    
    # Get threat level
    threat_level = get_user_input(
        "Threat Level",
        valid_options=THREAT_LEVELS,
        default="MEDIUM"
    )
    
    if threat_level.upper() == "SKIP":
        return False
    if threat_level.upper() == "QUIT":
        sys.exit(0)
    
    # Get product impact (use AI suggestion as default)
    default_impact = article.get('product_impact', 'General')
    if default_impact not in PRODUCT_IMPACTS:
        default_impact = 'General'
    
    product_impact = get_user_input(
        "Product Impact",
        valid_options=PRODUCT_IMPACTS,
        default=default_impact
    )
    
    if product_impact.upper() == "SKIP":
        return False
    if product_impact.upper() == "QUIT":
        sys.exit(0)
    
    # Get action recommendation
    action = get_user_input(
        "Action Recommendation",
        valid_options=ACTION_RECOMMENDATIONS,
        default="Watch"
    )
    
    if action.upper() == "SKIP":
        return False
    if action.upper() == "QUIT":
        sys.exit(0)
    
    # Get reviewer name
    reviewer = get_user_input("Your name/ID", default="editor")
    
    # Assign threat level
    success = assign_threat_level(
        article_id=article['id'],
        threat_level=threat_level,
        product_impact=product_impact,
        action_recommendation=action,
        reviewed_by=reviewer
    )
    
    if success:
        print(f"\n✓ Successfully reviewed article {article['id']}")
        return True
    else:
        print(f"\n✗ Failed to review article {article['id']}")
        return False


def main():
    """Main review interface loop."""
    print("CI Bot - Editor Review Interface")
    print("="*80)
    
    # Get pending reviews
    pending = get_pending_reviews()
    
    if not pending:
        print("\nNo articles pending review.")
        return
    
    print(f"\nFound {len(pending)} article(s) pending review.\n")
    
    reviewed_count = 0
    skipped_count = 0
    
    for i, article in enumerate(pending, 1):
        print(f"\n[{i}/{len(pending)}]")
        
        try:
            if review_article(article):
                reviewed_count += 1
            else:
                skipped_count += 1
        except KeyboardInterrupt:
            print("\n\nReview interrupted by user.")
            break
        except Exception as e:
            logger.error(f"Error reviewing article {article['id']}: {e}")
            print(f"\nError reviewing article: {e}")
            continue
    
    print(f"\n\nReview Summary:")
    print(f"  Reviewed: {reviewed_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"  Remaining: {len(pending) - reviewed_count - skipped_count}")


if __name__ == "__main__":
    main()

