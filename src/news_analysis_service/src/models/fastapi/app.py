"""Pydantic type definitions for FastAPI."""

from enum import StrEnum

from pydantic import BaseModel


class V1RouterTags(StrEnum):
    """Tags for the v1 API router."""

    OLLAMA = "Ollama"


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: str = "OK"
