"""RSS feed parser implementation."""

import html
import logging

import feedparser

from src.models.collection_targets import CollectionTarget, NewsItem

logger = logging.getLogger(__name__)


class RSSParser:
    """Parser for RSS feeds."""

    def parse(self, feed_data: str, target: CollectionTarget) -> list[NewsItem]:
        """Parse an RSS XML string into a list of NewsItems."""
        try:
            feed = feedparser.parse(feed_data)
        except Exception as e:
            logger.error(f"Failed to parse RSS feed for datasource {target.metadata.name}: {e}")
            return []

        if feed.bozo and hasattr(feed, "bozo_exception"):
            logger.warning(f"Feed parser bozo exception for {target.metadata.name}: {feed.bozo_exception}")

        items = []
        for entry in feed.entries:
            try:
                title = html.unescape(entry.get("title", ""))
                link = entry.get("link", "")
                description = html.unescape(entry.get("description", ""))
                pub_date = entry.get("published", "")

                if title and link:
                    items.append(
                        NewsItem(
                            title=title,
                            link=link,
                            description=description,
                            pub_date=pub_date,
                            metadata=target.metadata,
                        )
                    )

            except Exception as e:
                logger.error(f"Error parsing RSS entry from {target.metadata.name}: {e}")

        logger.debug(f"Parsed {len(items)} items from {target.metadata.name} feed.")
        return items
