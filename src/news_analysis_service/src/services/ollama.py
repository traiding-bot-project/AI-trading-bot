"""Ollama service implementation for generating AI completions."""

import logging
from typing import Any

from httpx import AsyncClient, HTTPStatusError

from src.constants import SERVICE_CLIENT_SESSION_TIMEOUT
from src.models.ollama_api import OllamaCompletionRequest, OllamaCompletionResponse, OllamaTagsResponse
from src.settings import settings
from src.settings.models.settings_model import OllamaImplementedEndpoints

logger = logging.getLogger(__name__)


class OllamaService:
    """Service for interacting with Ollama API to generate completions."""

    def __init__(self) -> None:
        """Initialize the OllamaService with an asynchronous HTTP client."""
        self.client = AsyncClient(timeout=SERVICE_CLIENT_SESSION_TIMEOUT)
        logger.info("OllamaService instance built")

    def get_endpoint_url(self, endpoint: OllamaImplementedEndpoints) -> str:
        """Construct the full endpoint URL for the Ollama API."""
        if endpoint.value not in settings.ai_model.deployments.ollama_deployments.api.implemented_endpoints:
            raise ValueError(f"Endpoint '{endpoint.value}' is not implemented in the Ollama API settings.")
        return f"{settings.ai_model.base_url}:{settings.ai_model.base_port}/api/{endpoint.value}"

    async def _send_get_request(self, url: str) -> Any:
        headers = {"Content-Type": "application/json"}
        response = await self.client.get(url, headers=headers)
        try:
            response.raise_for_status()
        except HTTPStatusError as e:
            raise RuntimeError(f"Request to Ollama API failed: {e}")
        return response.json()

    async def _send_post_request(self, url: str, body: OllamaCompletionRequest) -> Any:
        headers = {"Content-Type": "application/json"}
        request_data = body.model_dump()
        response = await self.client.post(url, json=request_data, headers=headers)
        try:
            response.raise_for_status()
        except HTTPStatusError as e:
            raise RuntimeError(f"Request to Ollama API failed: {e}")
        return response.json()

    async def list_models(self) -> OllamaTagsResponse:
        """Get the list of available models from the Ollama API."""
        url = self.get_endpoint_url(OllamaImplementedEndpoints.TAGS)
        logger.info(f"Sending GET request to Ollama API at {url}")
        response_data = await self._send_get_request(url)
        logger.debug(f"Response data: {response_data}")
        return OllamaTagsResponse(**response_data)

    async def generate_completion(self, request: OllamaCompletionRequest) -> OllamaCompletionResponse:
        """Generate a completion using the Ollama API based on the given request."""
        url = self.get_endpoint_url(OllamaImplementedEndpoints.GENERATE)
        logger.info(f"Sending POST request to Ollama API at {url}")
        logger.debug(f"Request data: {request.model_dump()}")
        response_data = await self._send_post_request(url, request)
        logger.debug(f"Response data: {response_data}")
        return OllamaCompletionResponse(**response_data)
