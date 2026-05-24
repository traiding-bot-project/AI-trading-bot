"""Qwen Service implementation for generating AI completions."""

import logging
from typing import Any

from httpx import AsyncClient, HTTPStatusError

from src.constants import SERVICE_CLIENT_SESSION_TIMEOUT
from src.models.qwen_api import (
    QwenCompletionRequest,
    QwenCompletionResponse,
    QwenModelsResponse,
)
from src.settings import settings
from src.settings.models.settings_model import QwenImplementedEndpoints

logger = logging.getLogger(__name__)


class QwenService:
    """Service for interacting with the Qwen API to generate AI completions."""

    def __init__(self) -> None:
        """Initialize the QwenService with an asynchronous HTTP client."""
        self.client = AsyncClient(timeout=SERVICE_CLIENT_SESSION_TIMEOUT)
        logger.info(
            f"QwenService initialized with timeout={SERVICE_CLIENT_SESSION_TIMEOUT}s"
        )

    def get_endpoint_url(self, endpoint: QwenImplementedEndpoints) -> str:
        """Construct the full endpoint URL for the Qwen API."""
        logger.debug(f"Constructing URL for endpoint: {endpoint.value}")
        if (
            endpoint.value
            not in settings.ai_model.deployments.qwen_deployments.api.implemented_endpoints
        ):
            logger.error(
                f"Endpoint '{endpoint.value}' is not implemented in Qwen API settings"
            )
            raise ValueError(
                f"Endpoint '{endpoint.value}' is not implemented in the Qwen API settings."
            )
        url = f"{settings.ai_model.base_url}:{settings.ai_model.base_port}/{endpoint.value}"
        logger.debug(f"Constructed endpoint URL: {url}")
        return url
    


    # TODO: what is this one for??? -> the same about ollama service
    async def _send_get_request(self, url: str) -> Any:
        """Send HTTP GET request to Qwen API and return parsed JSON response."""
        logger.debug(f"Sending GET request to: {url}")
        headers = {"Content-Type": "application/json"}
        response = await self.client.get(url, headers=headers)
        try:
            response.raise_for_status()
        except HTTPStatusError as e:
            logger.error(
                f"GET request to Qwen API failed with status {e.response.status_code}: {e}"
            )
            raise RuntimeError(f"Request to Qwen API failed: {e}")
        logger.debug("GET request successful")
        return response.json()
    


    # TODO: go through schemas QwenCompletionRequest -> they sure will be different
    async def _send_post_request(self, url: str, body: QwenCompletionRequest) -> Any:
        """Send HTTP POST request with body to Qwen API and return parsed JSON response."""
        logger.debug(f"Sending POST request to: {url}")
        headers = {"Content-Type": "application/json"}
        request_data = body.model_dump()
        logger.debug(f"POST request body size: {len(str(request_data))} bytes")
        response = await self.client.post(url, json=request_data, headers=headers)
        try:
            response.raise_for_status()
        except HTTPStatusError as e:
            logger.error(
                f"POST request to Qwen API failed with status {e.response.status_code}: {e}"
            )
            raise RuntimeError(f"Request to Qwen API failed: {e}")
        logger.debug("POST request successful")
        return response.json()
    



    # TODO: what is this one for??? -> the same about ollama service
    async def list_models(self) -> QwenModelsResponse:
        """Get the list of available models from the Qwen API."""
        logger.info("Fetching available models from Qwen API")
        url = self.get_endpoint_url(QwenImplementedEndpoints.MODELS)
        response_data = await self._send_get_request(url)
        logger.debug(
            f"Received model list with {len(response_data.get('data', []))} models"
        )
        return QwenModelsResponse(**response_data)

    async def generate_completion(
        self, request: QwenCompletionRequest
    ) -> QwenCompletionResponse:
        """Generate a completion using the Qwen API based on the given request."""
        logger.info(f"Generating completion with model: {request.model}")
        url = self.get_endpoint_url(QwenImplementedEndpoints.CHAT_COMPLETIONS)
        response_data = await self._send_post_request(url, request)
        logger.debug("Generated chat completion successfully.")
        return QwenCompletionResponse(**response_data)
