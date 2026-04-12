"""FastAPI router for handling Ollama API interactions."""

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Body, status
from src.interfaces import content_analyzer
from src.models.fastapi.app import V1RouterTags
from src.models.ollama_api import OllamaCompletionRequest, OllamaCompletionResponse, OllamaTagsResponse

logger = logging.getLogger(__name__)

ollama_router = APIRouter(prefix="/ollama", tags=[V1RouterTags.OLLAMA])


@ollama_router.post("/generate", response_model=OllamaCompletionResponse, status_code=status.HTTP_200_OK)
async def generate_completion(body: Annotated[OllamaCompletionRequest, Body(...)]) -> Any:
    """Endpoint to generate a completion using the Ollama AI model."""
    logger.info("POST /ollama/generate - Received completion generation request")
    logger.debug(f"Model requested: {body.model}")
    result = await content_analyzer.analyze_content(body)
    logger.debug(f"Completion generated successfully")
    return result


@ollama_router.get("/tags", response_model=OllamaTagsResponse, status_code=status.HTTP_200_OK)
async def list_models() -> Any:
    """Endpoint to list available models in the Ollama service."""
    logger.info("GET /ollama/tags - Received request to list available models")
    result = await content_analyzer.list_models()
    logger.debug(f"Successfully retrieved {len(result.models)} available models")
    return result
