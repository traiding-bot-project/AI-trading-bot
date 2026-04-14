"""Interface definitions for AI service interactions."""

from typing import Protocol

from src.models.action_union_types import AnalyzeContentRequest, AnalyzeContentResponse, ListModelsResponse


class AIService(Protocol):
    """Protocol for AI service interactions. Defines the expected interface for AI model interactions."""

    async def list_models(self) -> ListModelsResponse:
        """Get the list of available models from the AI service."""
        ...

    async def generate_completion(self, request: AnalyzeContentRequest) -> AnalyzeContentResponse:
        """Generate a completion based on the given request and return the response."""
        ...
