"""Pydantic models for Telegram bot broadcast operations."""

from pydantic import BaseModel


class BroadcastResponse(BaseModel):
    """Response model for a broadcast operation."""

    success: bool
