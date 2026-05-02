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


class URLSchema(StrEnum):
    """URL schemas for datasource connections."""

    HTTP = "http"
    HTTPS = "https"


class RegionCode(StrEnum):
    """Region codes for datasource organization.

    Represents geographic or logical regions where data sources are available.
    """

    PL = "pl"


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

    name: Annotated[
        str,
        Field(
            ...,
            title="Datasource Name",
            description="Unique name identifier for the datasource.",
        ),
    ]
    language: Annotated[
        str,
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
    root_url: Annotated[
        str,
        Field(
            ...,
            title="Root URL",
            description="Base URL for the datasource.",
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


class PolandDatasourcesConfig(StrictBaseModel):
    """Configuration for datasources specific to the Poland region."""

    pap: Annotated[
        DatasourceConfig,
        Field(
            ...,
            title="PAP Datasource",
            description="Configuration for the PAP datasource in Poland.",
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
