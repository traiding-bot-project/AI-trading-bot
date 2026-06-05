from typing import Annotated

from pydantic import Field, BaseModel

from market_intel_lib.models.custom_base_model import StrictBaseModel


class LibrarySettings(BaseModel):
    """Settings model for the shared library. Wraps Infisical settings
    and ignores other service-specific fields."""
    infisical: InfiscalSettings


class InfiscalConnectionSettings(StrictBaseModel):
    """Connection settings for Infiscal API."""

    url_schema: Annotated[
        str,
        Field(
            ...,
            title="Schema",
            description="URL schema (e.g., http, https) for connecting to Infiscal API.",
        ),
    ]
    host: Annotated[
        str,
        Field(
            ...,
            title="Host",
            description="Infiscal API host address.",
        ),
    ]
    port: Annotated[
        int,
        Field(
            ...,
            title="Port",
            description="Infiscal API port.",
        ),
    ]


class InfiscalAuthSettings(StrictBaseModel):
    """Authentication settings for Infiscal."""

    client_id: Annotated[
        str,
        Field(
            ...,
            title="Client ID",
            description="Infiscal client ID for authentication.",
        ),
    ]


class InfiscalProjectSettings(StrictBaseModel):
    """Project settings for Infiscal."""

    project_id: Annotated[
        str,
        Field(
            ...,
            title="Project ID",
            description="Infiscal project ID.",
        ),
    ]
    env_slug: Annotated[
        str,
        Field(
            ...,
            title="Environment Slug",
            description="Infiscal environment slug.",
        ),
    ]
    secret_path: Annotated[
        str,
        Field(
            ...,
            title="Secret Path",
            description="Path to secrets in Infiscal.",
        ),
    ]


class InfiscalSettings(StrictBaseModel):
    """Settings for Infiscal secret management service."""

    connection: Annotated[
        InfiscalConnectionSettings,
        Field(
            ...,
            title="Connection",
            description="Infiscal API connection settings.",
        ),
    ]
    auth: Annotated[
        InfiscalAuthSettings,
        Field(
            ...,
            title="Auth",
            description="Infiscal authentication settings.",
        ),
    ]
    project: Annotated[
        InfiscalProjectSettings,
        Field(
            ...,
            title="Project",
            description="Infiscal project settings.",
        ),
    ]
