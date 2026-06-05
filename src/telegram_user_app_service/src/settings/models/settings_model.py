"""Settings models for the Notification Service microservice."""

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


class DatabaseSettings(StrictBaseModel):
    """Settings for the database connection."""

    url_schema: Annotated[
        str,
        Field(
            ...,
            title="Schema",
            description="Database URL schema (e.g., postgresql, mysql).",
        ),
    ]
    host: Annotated[
        str,
        Field(
            ...,
            title="Host",
            description="Database host address.",
        ),
    ]
    port: Annotated[
        int,
        Field(
            ...,
            title="Port",
            description="Database port.",
        ),
    ]
    database: Annotated[
        str,
        Field(
            ...,
            title="Database Name",
            description="Name of the database to connect to.",
        ),
    ]
    username: Annotated[
        str,
        Field(
            ...,
            title="Username",
            description="Username for database authentication.",
        ),
    ]


class Settings(StrictBaseModel):
    """Main settings model for the Notification Service microservice."""

    service: ServiceSettings = Field(
        ...,
        title="Service settings",
        description="Configuration for the service runtime (host/port/environment).",
    )
    database: DatabaseSettings = Field(
        ...,
        title="Database settings",
        description="Configuration for the database connection.",
    )
