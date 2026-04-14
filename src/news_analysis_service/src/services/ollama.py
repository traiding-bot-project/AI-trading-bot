"""Ollama Service implementation for generating AI completions."""

import logging
from typing import Any

from httpx import AsyncClient, HTTPStatusError

from src.constants import SERVICE_CLIENT_SESSION_TIMEOUT
from src.models.ollama_api import OllamaCompletionRequest, OllamaCompletionResponse, OllamaTagsResponse
from src.settings import settings
from src.settings.models.settings_model import OllamaImplementedEndpoints

logger = logging.getLogger(__name__)


class OllamaService:
    """Service for interacting with the Ollama API to generate AI completions."""

    def __init__(self) -> None:
        """Initialize the OllamaService with an asynchronous HTTP client."""
        self.client = AsyncClient(timeout=SERVICE_CLIENT_SESSION_TIMEOUT)
        logger.info(f"OllamaService initialized with timeout={SERVICE_CLIENT_SESSION_TIMEOUT}s")

    def get_endpoint_url(self, endpoint: OllamaImplementedEndpoints) -> str:
        """Construct the full endpoint URL for the Ollama API."""
        logger.debug(f"Constructing URL for endpoint: {endpoint.value}")
        if endpoint.value not in settings.ai_model.deployments.ollama_deployments.api.implemented_endpoints:
            logger.error(f"Endpoint '{endpoint.value}' is not implemented in Ollama API settings")
            raise ValueError(f"Endpoint '{endpoint.value}' is not implemented in the Ollama API settings.")
        url = f"{settings.ai_model.base_url}:{settings.ai_model.base_port}/api/{endpoint.value}"
        logger.debug(f"Constructed endpoint URL: {url}")
        return url

    async def _send_get_request(self, url: str) -> Any:
        """Send HTTP GET request to Ollama API and return parsed JSON response."""
        logger.debug(f"Sending GET request to: {url}")
        headers = {"Content-Type": "application/json"}
        response = await self.client.get(url, headers=headers)
        try:
            response.raise_for_status()
        except HTTPStatusError as e:
            logger.error(f"GET request to Ollama API failed with status {e.response.status_code}: {e}")
            raise RuntimeError(f"Request to Ollama API failed: {e}")
        logger.debug("GET request successful")
        return response.json()

    async def _send_post_request(self, url: str, body: OllamaCompletionRequest) -> Any:
        """Send HTTP POST request with body to Ollama API and return parsed JSON response."""
        logger.debug(f"Sending POST request to: {url}")
        headers = {"Content-Type": "application/json"}
        request_data = body.model_dump()
        logger.debug(f"POST request body size: {len(str(request_data))} bytes")
        response = await self.client.post(url, json=request_data, headers=headers)
        try:
            response.raise_for_status()
        except HTTPStatusError as e:
            logger.error(f"POST request to Ollama API failed with status {e.response.status_code}: {e}")
            raise RuntimeError(f"Request to Ollama API failed: {e}")
        logger.debug("POST request successful")
        return response.json()

    async def list_models(self) -> OllamaTagsResponse:
        """Get the list of available models from the Ollama API."""
        logger.info("Fetching available models from Ollama API")
        url = self.get_endpoint_url(OllamaImplementedEndpoints.TAGS)
        response_data = await self._send_get_request(url)
        logger.debug(f"Received model list with {len(response_data.get('models', []))} models")
        return OllamaTagsResponse(**response_data)

    async def generate_completion(self, request: OllamaCompletionRequest) -> OllamaCompletionResponse:
        """Generate a completion using the Ollama API based on the given request."""
        logger.info(f"Generating completion with model: {request.model}")
        url = self.get_endpoint_url(OllamaImplementedEndpoints.GENERATE)
        response_data = await self._send_post_request(url, request)
        logger.debug(f"Generated completion with status done={response_data.get('done', False)}")
        return OllamaCompletionResponse(**response_data)
