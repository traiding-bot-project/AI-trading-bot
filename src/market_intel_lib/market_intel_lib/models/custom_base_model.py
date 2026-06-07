"""Custom base model for strict settings validation."""

from pydantic import BaseModel, ConfigDict


class StrictBaseModel(BaseModel):
    """Base model for strict settings validation.

    Enforces that unknown fields are rejected in TOML settings objects.
    """

    model_config = ConfigDict(extra="forbid")
