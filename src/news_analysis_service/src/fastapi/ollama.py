"""FastAPI router for handling Ollama API interactions."""

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, status
from src.analyzer import get_content_analyzer
from src.analyzer.content_analyzer import AIContentAnalyzer
from src.models.ai_types import (
    AnalyzeContentResponse,
    OllamaAnalyzeContentRequest,
)
from src.models.fastapi.app import V1RouterTags
from src.models.ollama_api import (
    OllamaModelsList,
)
from src.settings.models.settings_model import CompatibleAPI

content_analyzer = get_content_analyzer(CompatibleAPI.OLLAMA)

logger = logging.getLogger(__name__)

ollama_router = APIRouter(prefix="/ollama", tags=[V1RouterTags.OLLAMA])


def get_ollama_content_analyzer() -> AIContentAnalyzer:
    """Provide the Ollama content analyzer instance (overridable via FastAPI dependency overrides in tests)."""
    return content_analyzer


@ollama_router.post("/generate", response_model=AnalyzeContentResponse, status_code=status.HTTP_200_OK)
async def generate_completion(
    body: Annotated[OllamaAnalyzeContentRequest, Body(...)],
    analyzer: Annotated[AIContentAnalyzer, Depends(get_ollama_content_analyzer)],
) -> Any:
    """Endpoint to generate a completion using the Ollama AI model."""
    logger.info("POST /ollama/generate - Received completion generation request")
    logger.debug(f"Model requested: {body.model}")
    result = await analyzer.analyze_content(body)
    logger.debug("Completion generated successfully")
    return result


@ollama_router.get("/tags", response_model=OllamaModelsList, status_code=status.HTTP_200_OK)
async def list_models(
    analyzer: Annotated[AIContentAnalyzer, Depends(get_ollama_content_analyzer)],
) -> Any:
    """Endpoint to list available models in the Ollama service."""
    logger.info("GET /ollama/tags - Received request to list available models")
    result = await analyzer.list_models()
    logger.debug(f"Successfully retrieved models: {result}")
    return result
