"""Pydantic models for subscription token management in the Telegram user app service."""

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class SubscriptionToken(BaseModel):
    """Represents a subscription token for Telegram user onboarding."""

    id: Annotated[int | None, Field(default=None, title="Token ID")] = None
    token: Annotated[
        str, Field(..., title="Token", description="The generated subscription token.")
    ]
    user_id: Annotated[
        int | None,
        Field(
            default=None,
            title="User ID",
            description="Linked user ID once the token is activated.",
        ),
    ] = None
    created_at: Annotated[datetime, Field(..., title="Creation Timestamp")]
    activated_at: Annotated[
        datetime | None, Field(default=None, title="Activation Timestamp")
    ]
    expires_at: Annotated[datetime, Field(..., title="Expiration Timestamp")]

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
