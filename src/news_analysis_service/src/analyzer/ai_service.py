"""Interface definitions for AI service interactions."""

from typing import Protocol

from src.models.ai_types import (
    AnalyzeContentRequest,
    AnalyzeContentResponse,
)
from src.models.ollama_api import OllamaModelsList
from src.models.qwen_api import QwenModelsList


class AIService(Protocol):
    """Protocol defining the interface for AI service interactions."""

    async def list_models(self) -> OllamaModelsList | QwenModelsList:
        """Get the list of available models from the AI service."""
        ...

    async def generate_completion(self, request: AnalyzeContentRequest) -> AnalyzeContentResponse:
        """Generate a completion based on the given request and return the response."""
        ...
