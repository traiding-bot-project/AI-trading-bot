"""Protocol for datasource parsers."""

from typing import Protocol

from src.models.collection_targets import CollectionTarget, NewsItem


class DatasourceParserDefinition(Protocol):
    """Protocol defining the interface for datasource parsers."""

    def parse(self, feed_data: str, target: CollectionTarget) -> list[NewsItem]:
        """Parse raw content from a datasource into a list of NewsItem objects."""
        pass
