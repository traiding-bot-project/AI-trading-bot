"""Pydantic models for the Telegram Bot FastAPI endpoints."""

from pydantic import BaseModel, ConfigDict, Field


class BroadcastRequest(BaseModel):
    """Request model for broadcasting a message to Telegram users."""

    message: str = Field(..., alias="response")

    model_config = ConfigDict(populate_by_name=True)


class BroadcastResponse(BaseModel):
    """Response model for broadcasting a message to Telegram users."""

    success: bool
