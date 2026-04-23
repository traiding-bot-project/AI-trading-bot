"""Content analyzer model for AI-powered content analysis."""

import asyncio
import logging

from pydantic import BaseModel, ConfigDict, SkipValidation

from src.interfaces.ai_service import AIService
from src.models.action_union_types import AnalyzeContentRequest, AnalyzeContentResponse, ListModelsResponse

logger = logging.getLogger(__name__)


VALIDATE_AVAILABLE_MODELS_TIMEOUT = 3


class AIContentAnalyzer(BaseModel):
    """Content analyzer that uses an underlying AI service to analyze content."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    service: SkipValidation[AIService]

    async def log_available_models(self) -> None:
        """Log available models — call this from inside an async context."""
        try:
            response = await asyncio.wait_for(self.service.list_models(), timeout=VALIDATE_AVAILABLE_MODELS_TIMEOUT)
            model_names = [model.name for model in response.models]
            logger.info(f"Available models for AI Content Analyzer: {model_names}")
        except TimeoutError:
            logger.error("Timeout while fetching available models")
        except Exception as e:
            logger.error(f"Failed to log available models: {e}")

    async def analyze_content(self, request: AnalyzeContentRequest) -> AnalyzeContentResponse:
        """Analyze content using the underlying AI service."""
        logger.info(f"Analyzing content with model: {request.model}")
        result = await self.service.generate_completion(request)
        logger.debug("Content analysis completed")
        return result

    async def list_models(self) -> ListModelsResponse:
        """List available models from the underlying AI service."""
        logger.info("Listing available AI models")
        result = await self.service.list_models()
        logger.debug(f"Retrieved {len(result.models)} available models")
        return result
