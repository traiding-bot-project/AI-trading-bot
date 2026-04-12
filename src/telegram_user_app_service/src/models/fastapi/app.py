"""Pydantic type definitions for FastAPI."""

from enum import StrEnum

from pydantic import BaseModel


class V1RouterTags(StrEnum):
    """Enum for FastAPI router tags used for API documentation."""

    TELEGRAM_BOT = "Telegram Bot"
    USER_SERVICE = "User Service"


class HealthCheck(BaseModel):
    """Response model for health check endpoint."""

    status: str = "OK"
