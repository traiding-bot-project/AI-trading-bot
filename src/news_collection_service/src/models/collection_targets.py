"""Models for the parsed news items."""

from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, Field

from src.settings.models.settings_model import DatasourceType, SupportedLanguages


class ExtractionMethods(StrEnum):
    """Enum for tracking which extraction method was used for a news item."""

    TRAFILATURA = "trafilatura"
    BEAUTIFULSOUP = "beautifulsoup"
    NONE = "none"


class DataSourceMetadata(BaseModel):
    """Model representing metadata about the RSS feed for a news item."""

    name: Annotated[
        str,
        Field(
            title="Datasource Name",
            description="The name of the datasource (e.g., 'PAP', 'Reuters').",
        ),
    ]
    language: Annotated[
        SupportedLanguages,
        Field(
            title="Language",
            description="The language associated with the datasource (e.g., 'pl', 'en').",
        ),
    ]
    region: Annotated[
        str,
        Field(
            title="Region",
            description="The region associated with the datasource (e.g., 'pl', 'us').",
        ),
    ]
    extraction_method: Annotated[
        ExtractionMethods,
        Field(
            ExtractionMethods.NONE,
            title="Extraction Method",
            description="The method used to extract the news item content",
        ),
    ] = ExtractionMethods.NONE


class NewsItem(BaseModel):
    """Model representing a parsed news item."""

    title: Annotated[
        str, Field(title="Title", description="The title of the news item")
    ]
    link: Annotated[str, Field(title="Link", description="The URL of the news item")]
    description: Annotated[
        str | None,
        Field(
            None,
            title="Description",
            description="A brief description of the news item",
        ),
    ]
    pub_date: Annotated[
        str,
        Field(
            title="Publication Date",
            description="The publication date of the news item",
        ),
    ]
    raw_content: Annotated[
        str | None,
        Field(None, title="Raw Content", description="Text from news source"),
    ] = None
    prepared_content: Annotated[
        str | None,
        Field(
            None,
            title="Prepared Content",
            description="The cleaned content ready for LLM input",
        ),
    ] = None
    metadata: Annotated[
        DataSourceMetadata,
        Field(title="Datasource Metadata", description="Metadata about the datasource"),
    ]


class CollectionTarget(BaseModel):
    """Internal model for tracking specific collection endpoints and their metadata."""

    url: Annotated[str, Field(title="Target URL", description="The full URL to poll.")]
    domain: Annotated[
        str,
        Field(title="Domain", description="The root domain used for rate limiting."),
    ]
    datasource_type: Annotated[DatasourceType, Field(title="Type", description="RSS, API, etc.")]
    category: Annotated[str, Field(title="Category")]
    ignore_routes: Annotated[
        list[str],
        Field(title="Ignore Routes", description="Routes to ignore for this target."),
    ]
    metadata: Annotated[
        DataSourceMetadata,
        Field(title="Datasource Metadata", description="Metadata about the datasource"),
    ]
