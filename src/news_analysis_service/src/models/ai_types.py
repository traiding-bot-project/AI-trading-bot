"""Union type definitions for AI service interactions."""

from typing import Annotated

from pydantic import BaseModel, Field

from src.settings.models.settings_model import (
    OllamaSupportedModels,
    QwenSupportedModels,
)


class AnalyzeContentRequest(BaseModel):
    """Request model for content analysis by the AI service."""

    model: Annotated[
        OllamaSupportedModels | QwenSupportedModels,
        Field(
            ...,
            title="The AI model to use for content analysis (depends on the deployment)",
        ),
    ]
    prompt: Annotated[
        str,
        Field(..., title="The prompt to send to the AI model for content analysis"),
    ]


class OllamaAnalyzeContentRequest(AnalyzeContentRequest):
    """Request model for content analysis using the Ollama API."""

    model: Annotated[
        OllamaSupportedModels,
        Field(
            ...,
            title="The Ollama AI model to use for content analysis",
        ),
    ]


class QwenAnalyzeContentRequest(AnalyzeContentRequest):
    """Request model for content analysis using the Qwen API."""

    model: Annotated[
        QwenSupportedModels,
        Field(
            ...,
            title="The Qwen AI model to use for content analysis",
        ),
    ]


class AnalyzeContentResponse(BaseModel):
    """Response model for content analysis results from the AI service."""

    response: Annotated[
        str,
        Field(
            ...,
            title="The generated response from the AI model based on the provided prompt",
        ),
    ]
