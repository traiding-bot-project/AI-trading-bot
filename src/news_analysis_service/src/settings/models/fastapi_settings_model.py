"""Settings model for configuring the FastAPI application."""

from typing import Annotated

from pydantic import Field

from src.settings.models.custom_base_model import StrictBaseModel


class FastAPISettings(StrictBaseModel):
    """Settings model for configuring the FastAPI application."""

    host: Annotated[
        str,
        Field(
            ...,
            title="Host",
            description="Host IP address to bind the service.",
        ),
    ]
    port: Annotated[
        int,
        Field(
            ...,
            ge=1,
            le=65535,
            title="Port",
            description="TCP port to bind the service.",
        ),
    ]
