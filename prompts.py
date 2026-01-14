"""LLM prompt templates for article classification."""
from typing import Dict


def get_classification_prompt(article_text: str) -> str:
    """Generate classification prompt for Claude API.
    
    Uses the prompt template from PRD Appendix Section 13.
    """
    prompt = """You are a competitive intelligence analyst for Alkimi, an AdTech company with two key products:
1. AMP (Advertiser Management Platform) - unified multi-DSP campaign management with AI reporting
2. Zero-Day Payments - blockchain-based instant publisher settlement

Analyze the following article and determine:
1. RELEVANCE (1-5): How relevant is this to AI/automation in advertising?
2. CATEGORY: Campaign Automation | Cross-DSP Tools | AI Reporting/Analytics | Payment Innovation | Web3 Advertising | Other
3. PRODUCT_IMPACT: AMP | Zero-Day | Both | General
4. SUMMARY: 2-sentence summary focusing on competitive implications for Alkimi

Article:
{article_text}

Respond in JSON format with the following structure:
{{
    "relevance": <1-5 integer>,
    "category": "<category name>",
    "product_impact": "<AMP|Zero-Day|Both|General>",
    "summary": "<2-sentence summary>"
}}""".format(article_text=article_text[:8000])  # Limit article text to avoid token limits
    
    return prompt


def get_summary_prompt(article_text: str) -> str:
    """Generate a summary prompt for articles that need additional context."""
    prompt = """Summarize the following article in 2-3 sentences, focusing on:
- Key competitive developments
- AI/automation capabilities mentioned
- Payment or settlement innovations
- Implications for AdTech companies

Article:
{article_text}""".format(article_text=article_text[:8000])
    
    return prompt

