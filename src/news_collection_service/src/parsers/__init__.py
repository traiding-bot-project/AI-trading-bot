"""Parser module for the News Collection service."""

from src.parsers.parser_definition import DatasourceParserDefinition
from src.parsers.rss_parser import RSSParser


def get_parser(datasource_type: str) -> DatasourceParserDefinition:
    """Factory function to retrieve the appropriate parser based on the name."""
    parsers = {
        "rss": RSSParser(),
    }
    parser = parsers.get(datasource_type.lower())
    if not parser:
        raise ValueError(f"Parser '{datasource_type}' is not supported.")
    return parser
