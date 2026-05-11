"""Settings models for the Sentiment Analysis Service microservice."""

from enum import StrEnum
from typing import Annotated

from pydantic import Field

from src.settings.models.custom_base_model import StrictBaseModel


class DeploymentType(StrEnum):
    """Deployment types for the service.

    Can be used to differentiate between different deployment configurations or settings.
    """

    DEV = "dev"
    PROD = "prod"


class EnvironmentType(StrEnum):
    """Runtime environment types for the service.

    Can be used to enable/disable certain features or logging levels based on the environment.
    """

    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class LoggingLevel(StrEnum):
    """Logging levels for the service.

    Can be used to configure the logging level of the application based on the deployment or environment.
    """

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class DatasourceType(StrEnum):
    """Datasource types supported by the service."""

    RSS = "rss"
    API = "api"
    TEXT = "text"


class URLSchema(StrEnum):
    """URL schemas for datasource connections."""

    HTTP = "http"
    HTTPS = "https"


class SupportedLanguages(StrEnum):
    """Supported languages for the datasources."""

    POLISH = "pl"


class ServiceSettings(StrictBaseModel):
    """Settings for the service runtime."""

    deployment: Annotated[
        DeploymentType,
        Field(
            ...,
            title="Deployment",
            description="Deployment type (dev, staging, prod).",
        ),
    ]
    environment: Annotated[
        EnvironmentType,
        Field(
            ...,
            title="Environment",
            description="Runtime environment name.",
        ),
    ]
    logging_level: Annotated[
        LoggingLevel,
        Field(
            ...,
            title="Logging Level",
            description="Logging level for the application.",
        ),
    ]


class DatasourceConfig(StrictBaseModel):
    """Configuration for a single datasource within a region."""

    language: Annotated[
        SupportedLanguages,
        Field(
            ...,
            title="Language",
            description="Language code for the datasource content.",
        ),
    ]
    type: Annotated[
        DatasourceType,
        Field(
            ...,
            title="Datasource Type",
            description="Type of datasource.",
        ),
    ]
    url_schema: Annotated[
        URLSchema,
        Field(
            ...,
            title="URL Schema",
            description="URL schema to use for requests (http, https).",
        ),
    ]
    domain: Annotated[
        str,
        Field(
            ...,
            title="Domain",
            description="Domain name for the datasource.",
        ),
    ]
    data_route: Annotated[
        str,
        Field(
            ...,
            title="Data Route",
            description="API route or path to fetch data from.",
        ),
    ]
    available_categories: Annotated[
        list[str],
        Field(
            ...,
            title="Available Categories",
            description="List of available categories for this datasource.",
        ),
    ]
    ignore_routes: Annotated[
        list[str],
        Field(
            None,
            title="Ignore Routes",
            description="List of routes to ignore for this datasource.",
        ),
    ]
    endpoint: Annotated[
        str | None,
        Field(
            None,
            title="Endpoint",
            description="Specific endpoint for fetching data, if the request scheme is unconventional.",
        ),
    ]


class PolandDatasourcesConfig(StrictBaseModel):
    """Configuration for datasources specific to the Poland region."""

    pap_mediaroom: Annotated[
        DatasourceConfig,
        Field(
            ...,
            title="PAP Datasource",
            description="Configuration for the PAP datasource in Poland.",
        ),
    ]
    bankier: Annotated[
        DatasourceConfig,
        Field(
            ...,
            title="Bankier Datasource",
            description="Configuration for the Bankier datasource in Poland.",
        ),
    ]
    money: Annotated[
        DatasourceConfig,
        Field(
            ...,
            title="Money.pl Datasource",
            description="Configuration for the Money.pl datasource in Poland.",
        ),
    ]


class DatasourcesConfig(StrictBaseModel):
    """Configuration container for all regions and their datasources."""

    pl: Annotated[
        PolandDatasourcesConfig,
        Field(
            ...,
            title="Poland Datasources",
            description="Configuration for all datasources in the Poland region.",
        ),
    ]


class Settings(StrictBaseModel):
    """Main settings model for the Sentiment Analysis Service microservice."""

    service: Annotated[
        ServiceSettings,
        Field(
            ...,
            title="Service settings",
            description="Configuration for the service runtime (host/port/environment).",
        ),
    ]
    datasource: Annotated[
        DatasourcesConfig,
        Field(
            ...,
            title="Datasources",
            description="Configuration for all datasources organized by regions.",
        ),
    ]
