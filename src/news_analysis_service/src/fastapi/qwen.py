"""FastAPI router for handling Qwen API interactions."""

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Body, status
from src.interfaces import content_analyzer
from src.models.fastapi.app import V1RouterTags
from src.models.qwen_api import (
    QwenCompletionRequest,
    QwenCompletionResponse,
    QwenModelsResponse,
)

logger = logging.getLogger(__name__)

qwen_router = APIRouter(prefix="/qwen", tags=[V1RouterTags.QWEN])


@qwen_router.post("/generate", response_model=QwenCompletionResponse, status_code=status.HTTP_200_OK)
async def generate_completion(
    body: Annotated[QwenCompletionRequest, Body(...)],
) -> Any:
    """Endpoint to generate a completion using the Qwen AI model."""
    logger.info("POST /qwen/generate - Received completion generation request")
    logger.debug(f"Model requested: {body.model}")
    result = await content_analyzer.analyze_content(body)
    logger.debug("Completion generated successfully")
    return result


@qwen_router.get("/tags", response_model=QwenModelsResponse, status_code=status.HTTP_200_OK)
async def list_models() -> Any:
    """Endpoint to list available models in the Qwen service."""
    logger.info("GET /qwen/tags - Received request to list available models")
    result = await content_analyzer.list_models()
    model_list = [model.id for model in result.data]
    logger.debug(f"Successfully retrieved {len(model_list)} available models")
    return result
