"""Content analyzer model for AI-powered content analysis."""

import logging

from src.analyzer.ai_service import AIService
from src.models.action_union_types import (
    AnalyzeContentRequest,
    AnalyzeContentResponse,
)
from src.models.ollama_api import OllamaModelsList
from src.models.qwen_api import QwenModelsList

logger = logging.getLogger(__name__)


VALIDATE_AVAILABLE_MODELS_TIMEOUT = 3


class AIContentAnalyzer:
    """Content analyzer that uses an underlying AI service to analyze content."""

    def __init__(self, service: AIService):
        """Initialize the content analyzer with the given AI service."""
        self._service = service

    async def analyze_content(self, request: AnalyzeContentRequest) -> AnalyzeContentResponse:
        """Analyze content using the underlying AI service."""
        logger.info(f"Analyzing content with model: {request.model}")
        result = await self._service.generate_completion(request)
        logger.debug("Content analysis completed")
        return result

    async def list_models(self) -> OllamaModelsList | QwenModelsList:
        """List available models from the underlying AI service."""
        logger.info("Listing available AI models")
        result = await self._service.list_models()
        logger.debug(f"Retrieved models: {result}")
        return result
