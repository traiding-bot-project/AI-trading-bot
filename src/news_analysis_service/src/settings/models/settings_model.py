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


class OllamaImplementedEndpoints(StrEnum):
    """Implemented endpoints for the Ollama API.

    These should correspond to the endpoints available in the Ollama API.
    """

    TAGS = "tags"
    SHOW = "show"
    CHAT = "chat"
    GENERATE = "generate"
    EMBEDDINGS = "embeddings"


class CompatibleAPI(StrEnum):
    """Compatible API providers for the AI model. Can be used to determine which API client to use for requests."""

    OLLAMA = "ollama"


class OllamaSupportedModels(StrEnum):
    """Supported Ollama models for the news analysis service.

    These should correspond to the model identifiers used by the Ollama API.
    """

    LLAMA32_1B_Q8_0 = "docker.io/ai/llama3.2:1B-Q8_0"


class ModelApi(StrictBaseModel):
    """API compatibility and implemented endpoints for a specific AI model."""

    compatible_api: Annotated[CompatibleAPI, Field(..., title="Compatible API provider for the model")]
    implemented_endpoints: Annotated[
        list[OllamaImplementedEndpoints],
        Field(..., title="List of implemented endpoints for the model in the compatible API"),
    ]


class OllamaSupportedDeployments(StrictBaseModel):
    """Supported Ollama models for the news analysis service.

    These should correspond to the model identifiers used by the Ollama API.
    """

    ollama_models: Annotated[list[OllamaSupportedModels], Field(..., title="Ollama Models")]
    api: Annotated[ModelApi, Field(..., title="API compatibility and implemented endpoints for the model")]


class SupportedDeployments(StrictBaseModel):
    """Supported AI models for the sentiment analysis service.

    These should correspond to model identifiers used by the AI backend.
    """

    ollama_deployments: Annotated[OllamaSupportedDeployments, Field(..., title="Ollama Models and API compatibility")]


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


class AIModelSettings(StrictBaseModel):
    """Settings related to the AI model connection and configuration."""

    deployments: Annotated[SupportedDeployments, Field(..., title="Supported AI models and their API compatibility")]
    base_url: Annotated[
        str,
        Field(
            ...,
            title="Base URL",
            description="Base URL for the AI API endpoint.",
        ),
    ]
    base_port: Annotated[
        int,
        Field(
            ...,
            ge=1,
            le=65535,
            title="Base Port",
            description="Port for AI API requests.",
        ),
    ]


class Settings(StrictBaseModel):
    """Main settings model for the Sentiment Analysis Service microservice."""

    service: ServiceSettings = Field(
        ...,
        title="Service settings",
        description="Configuration for the service runtime (host/port/environment).",
    )
    ai_model: AIModelSettings = Field(
        ...,
        title="AI model settings",
        description="Configuration for the AI model connection settings.",
    )
