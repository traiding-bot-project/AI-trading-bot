"""Financial analysis prompt builder for Telegram MarkdownV2 formatting."""

from src.models.news_items import NewsItem
from src.news_analysis_service.src.prompts.builder import load_and_format_prompt


def build_financial_analysis_prompt(news_item: NewsItem) -> str:
    """Build a financial analysis prompt from a NewsItem.

    Args:
        news_item: The NewsItem to analyze

    Returns:
        A formatted prompt string ready to send to an LLM
    """
    return load_and_format_prompt(
        "analyze_news.md",
        news_item=news_item,
        metadata=news_item.metadata,
        description=news_item.description or "N/A",
        prepared_content=news_item.prepared_content or "N/A"
    )
