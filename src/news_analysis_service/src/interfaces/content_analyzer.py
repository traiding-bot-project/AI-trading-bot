"""Model for the Ollama service implementation used in the AI Content Analyzer."""

from pydantic import BaseModel, ConfigDict, SkipValidation

from src.interfaces.ai_service import AIService
from src.models.action_union_types import AnalyzeContentRequest, AnalyzeContentResponse, ListModelsResponse


class AIContentAnalyzer(BaseModel):
    """Content analyzer that uses an underlying AI service to analyze content based on the given request."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    service: SkipValidation[AIService]

    async def analyze_content(self, request: AnalyzeContentRequest) -> AnalyzeContentResponse:
        """Analyze content using the underlying AI service based on the given request."""
        return await self.service.generate_completion(request)

    async def list_models(self) -> ListModelsResponse:
        """List available models using the underlying AI service."""
        return await self.service.list_models()
