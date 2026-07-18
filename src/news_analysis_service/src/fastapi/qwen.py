"""FastAPI router for handling Qwen API interactions."""

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, status
from src.analyzer import get_content_analyzer
from src.analyzer.content_analyzer import AIContentAnalyzer
from src.models.ai_types import (
    AnalyzeContentResponse,
    QwenAnalyzeContentRequest,
)
from src.models.fastapi.app import V1RouterTags
from src.models.qwen_api import (
    QwenModelsList,
)
from src.settings.models.settings_model import CompatibleAPI

content_analyzer = get_content_analyzer(CompatibleAPI.QWEN)

logger = logging.getLogger(__name__)

qwen_router = APIRouter(prefix="/qwen", tags=[V1RouterTags.QWEN])


def get_qwen_content_analyzer() -> AIContentAnalyzer:
    """Provide the Qwen content analyzer instance (overridable via FastAPI dependency overrides in tests)."""
    return content_analyzer


@qwen_router.post("/generate", response_model=AnalyzeContentResponse, status_code=status.HTTP_200_OK)
async def generate_completion(
    body: Annotated[QwenAnalyzeContentRequest, Body(...)],
    analyzer: Annotated[AIContentAnalyzer, Depends(get_qwen_content_analyzer)],
) -> Any:
    """Endpoint to generate a completion using the Qwen AI model."""
    logger.info("POST /qwen/generate - Received completion generation request")
    logger.debug(f"Model requested: {body.model}")
    result = await analyzer.analyze_content(body)
    logger.debug("Completion generated successfully")
    return result


@qwen_router.get("/tags", response_model=QwenModelsList, status_code=status.HTTP_200_OK)
async def list_models(
    analyzer: Annotated[AIContentAnalyzer, Depends(get_qwen_content_analyzer)],
) -> Any:
    """Endpoint to list available models in the Qwen service."""
    logger.info("GET /qwen/tags - Received request to list available models")
    result = await analyzer.list_models()
    logger.debug(f"Successfully retrieved models: {result}")
    return result
