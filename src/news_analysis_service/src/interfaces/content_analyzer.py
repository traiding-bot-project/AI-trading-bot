"""Content analyzer model for AI-powered content analysis."""

import logging

from pydantic import BaseModel, ConfigDict, SkipValidation

from src.interfaces.ai_service import AIService
from src.models.action_union_types import AnalyzeContentRequest, AnalyzeContentResponse, ListModelsResponse

logger = logging.getLogger(__name__)


class AIContentAnalyzer(BaseModel):
    """Content analyzer that uses an underlying AI service to analyze content."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    service: SkipValidation[AIService]

    async def analyze_content(self, request: AnalyzeContentRequest) -> AnalyzeContentResponse:
        """Analyze content using the underlying AI service."""
        logger.info(f"Analyzing content with model: {request.model}")
        result = await self.service.generate_completion(request)
        logger.debug(f"Content analysis completed")
        return result

    async def list_models(self) -> ListModelsResponse:
        """List available models from the underlying AI service."""
        logger.info("Listing available AI models")
        result = await self.service.list_models()
        logger.debug(f"Retrieved {len(result.models)} available models")
        return result
