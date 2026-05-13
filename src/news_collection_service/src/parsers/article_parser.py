"""Module for parsing article content from URLs."""

import html
import logging
import re

import trafilatura
from bs4 import BeautifulSoup

from src.models.collection_targets import ExtractionMethods, NewsItem

logger = logging.getLogger(__name__)


class ArticleParser:
    """Cleans raw HTML from a NewsItem and prepares it for LLM consumption."""

    def parse(self, item: NewsItem) -> NewsItem:
        """Parse the raw content of a news item and prepare it for LLM consumption."""
        body, method = self._extract_body(item)
        body = self._collapse_whitespace(body)
        body = html.unescape(body)

        item.prepared_content = body
        item.metadata.extraction_method = method

        return item

    def _extract_body(self, item: NewsItem) -> tuple[str, ExtractionMethods]:
        if item.raw_content:
            text = self._extract_with_trafilatura(item.raw_content)
            if text:
                return text, ExtractionMethods.TRAFILATURA

            text = self._extract_with_bs4(item.raw_content)
            if text:
                return text, ExtractionMethods.BEAUTIFULSOUP

            logger.warning(f"Both extractors returned empty for {item.link} — falling back to description")

        logger.warning(f"No extractable content for {item.link}")
        return "", ExtractionMethods.NONE

    def _extract_with_trafilatura(self, html: str) -> str:
        try:
            result = trafilatura.extract(
                html,
                no_fallback=False,
                include_comments=False,
                include_tables=True,
                deduplicate=True,
            )
            return result.strip() if result else ""
        except Exception:
            logger.exception("trafilatura extraction failed")
            return ""

    def _extract_with_bs4(self, html: str) -> str:
        try:
            soup = BeautifulSoup(html, "lxml")
            for tag in soup(
                ["script", "style", "nav", "header", "footer", "aside", "form", "button", "svg", "noscript"]
            ):
                tag.decompose()
            text = soup.get_text(separator="\n", strip=True)
            return self._collapse_whitespace(text)
        except Exception:
            logger.exception("BeautifulSoup extraction failed")
            return ""

    @staticmethod
    def _collapse_whitespace(text: str) -> str:
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" {2,}", " ", text)
        return text.strip()
