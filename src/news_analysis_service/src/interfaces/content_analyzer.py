"""Model for the Ollama service implementation used in the AI Content Analyzer."""

import asyncio
import logging
from typing import Self

from pydantic import BaseModel, ConfigDict, SkipValidation, model_validator

from src.interfaces.ai_service import AIService
from src.models.action_union_types import AnalyzeContentRequest, AnalyzeContentResponse, ListModelsResponse

logger = logging.getLogger(__name__)


VALIDATE_AVAILABLE_MODELS_TIMEOUT = 3


class AIContentAnalyzer(BaseModel):
    """Content analyzer that uses an underlying AI service to analyze content based on the given request."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    service: SkipValidation[AIService]

    @model_validator(mode="after")
    def vaidate_available_models(self) -> Self:
        """Check if the underlying AI service has available models."""
        try:
            logger.info("Logging available models for AI Content Analyzer")
            response = asyncio.run(
                asyncio.wait_for(self.service.list_models(), timeout=VALIDATE_AVAILABLE_MODELS_TIMEOUT)
            )
            model_names = [model.name for model in response.models]
            logger.info(f"Available models for AI Content Analyzer: {model_names}")
            return self
        except TimeoutError:
            logger.error("Timeout while fetching available models for AI Content Analyzer")
            return self
        except Exception as e:
            logger.error(f"Failed to log available models: {e}")
            return self

    async def analyze_content(self, request: AnalyzeContentRequest) -> AnalyzeContentResponse:
        """Analyze content using the underlying AI service based on the given request."""
        return await self.service.generate_completion(request)

    async def list_models(self) -> ListModelsResponse:
        """List available models using the underlying AI service."""
        return await self.service.list_models()
