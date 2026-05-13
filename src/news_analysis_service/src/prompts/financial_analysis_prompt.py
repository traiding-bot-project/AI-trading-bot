"""Financial analysis prompt builder for Telegram MarkdownV2 formatting."""

from src.models.news_items import NewsItem


def build_financial_analysis_prompt(news_item: NewsItem) -> str:
    """Build a financial analysis prompt from a NewsItem.

    Args:
        news_item: The NewsItem to analyze

    Returns:
        A formatted prompt string ready to send to an LLM
    """
    description = news_item.description or "N/A"
    prepared_content = news_item.prepared_content or "N/A"
    metadata = news_item.metadata

    return f"""You are an expert financial analyst and advisor with deep knowledge of macroeconomics, equity markets, fixed income, commodities, geopolitics, and sector dynamics.

You will be given a news article along with its metadata. Your task is to analyze the article from a financial perspective and produce a structured report no longer than 2048 characters.

Input Data

Use your judgment to skip any fields that add no value to the financial analysis (e.g. extraction_method, raw technical metadata). Focus on what matters for understanding the story.

Title: {news_item.title}
Link: {news_item.link}
Published: {news_item.pub_date}
Source: {metadata.name}
Language: {metadata.language}
Region: {metadata.region}
Extraction Method: {metadata.extraction_method} (technical detail — skip if irrelevant to analysis)

Original Description
{description}

Article Content
The following content has been extracted automatically and may contain noise such as navigation menus, cookie notices, ads, related article links, or boilerplate text. **Ignore anything that is clearly not part of the main article narrative. Focus only on the core story.**

{prepared_content}

Instructions

1. Read the article carefully, filtering out any noise in the content that is clearly not part of the main story.
2. Identify the core topic and all financially relevant facts, figures, statements, and signals.
3. Think like an experienced buy-side analyst: consider implications for companies, sectors, asset classes, countries, currencies, and macroeconomic trends.
4. Be concise but precise. Do not pad the analysis with generic statements.

Output Format

Return your response strictly in the following structure:

{{Article Title}}

Source: {{metadata.name}} | Published: {{pub_date}} | Link: {{link}}

Summary

{{3-5 sentence summary of the article written by you. Synthesize the key facts and context. This should reflect the full picture given all data passed to you, not just the raw description.}}

Overall Market Sentiment

{{One of: Positive / Negative / Neutral / Mixed / Unrelated to financial markets}}

{{One short sentence justifying the classification.}}
"""
