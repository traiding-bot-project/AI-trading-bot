"""Defines the User model for the Telegram User App Service."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator


class User(BaseModel):
    """Represents a user in the Telegram User App Service."""

    id: Annotated[int | None, Field(default=None, title="User ID", description="Unique identifier for the user.")]
    first_name: Annotated[str, Field(..., title="First Name", description="User's first name.")]
    last_name: Annotated[str, Field(..., title="Last Name", description="User's last name.")]
    username: Annotated[str, Field(..., title="Username", description="User's username.")]
    chat_id: Annotated[int, Field(..., title="Chat ID", description="Telegram chat ID for the user.")]
    is_subscribed: Annotated[
        bool,
        Field(default=False, title="Is Subscribed", description="Indicates if the user is subscribed to the bot."),
    ]

    @field_validator("last_name", mode="before")
    @classmethod
    def replace_none_with_empty_string(cls, v: str | None) -> str:
        """Replace None with an empty string for last_name."""
        return v if v is not None else ""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class UserFilters(BaseModel):
    """Filters for listing users."""

    is_subscribed: bool | None = None

    model_config = ConfigDict(extra="forbid")
