"""Qwen Service implementation for generating AI completions."""

import logging
from typing import Any

from httpx import AsyncClient, HTTPStatusError

from src.constants import SERVICE_CLIENT_SESSION_TIMEOUT
from src.models.ai_types import AnalyzeContentRequest, AnalyzeContentResponse
from src.models.qwen_api import (
    ChatMessage,
    ChatMessageRole,
    QwenCompletionRequest,
    QwenCompletionResponse,
    QwenModelsList,
    QwenModelsResponse,
)
from src.settings import settings
from src.settings.models.settings_model import (
    QwenImplementedEndpoints,
    QwenSupportedModels,
)

logger = logging.getLogger(__name__)


class QwenService:
    """Service for interacting with the Qwen API to generate AI completions."""

    def __init__(self) -> None:
        """Initialize the QwenService with an asynchronous HTTP client."""
        self.client = AsyncClient(timeout=SERVICE_CLIENT_SESSION_TIMEOUT)
        logger.info(f"QwenService initialized with timeout={SERVICE_CLIENT_SESSION_TIMEOUT}s")

    def get_endpoint_url(self, endpoint: QwenImplementedEndpoints) -> str:
        """Construct the full endpoint URL for the Qwen API."""
        logger.debug(f"Constructing URL for endpoint: {endpoint.value}")
        if endpoint.value not in settings.ai_model.deployments.qwen_deployments.api.implemented_endpoints:
            logger.error(f"Endpoint '{endpoint.value}' is not implemented in Qwen API settings")
            raise ValueError(f"Endpoint '{endpoint.value}' is not implemented in the Qwen API settings.")
        url = f"{settings.ai_model.base_url}:{settings.ai_model.base_port}/{endpoint.value}"
        logger.debug(f"Constructed endpoint URL: {url}")
        return url

    async def _send_get_request(self, url: str) -> Any:
        """Send HTTP GET request to Qwen API and return parsed JSON response."""
        logger.debug(f"Sending GET request to: {url}")
        headers = {"Content-Type": "application/json"}
        response = await self.client.get(url, headers=headers)
        try:
            response.raise_for_status()
        except HTTPStatusError as e:
            logger.error(f"GET request to Qwen API failed with status {e.response.status_code}: {e}")
            raise RuntimeError(f"Request to Qwen API failed: {e}")
        logger.debug("GET request successful")
        return response.json()

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
            error_details = response.text
            logger.error(
                f"POST request to Qwen API failed with status {e.response.status_code}: {e}. Details: {error_details}"
            )
            raise RuntimeError(f"Request to Qwen API failed: {e}. Details: {error_details}")
        logger.debug("POST request successful")
        return response.json()

    async def list_models(self) -> QwenModelsList:
        """Get the list of available models from the Qwen API."""
        logger.info("Fetching available models from Qwen API")
        url = self.get_endpoint_url(QwenImplementedEndpoints.MODELS)
        response_data = QwenModelsResponse.model_validate(await self._send_get_request(url))
        supported_models = settings.ai_model.deployments.qwen_deployments.models
        models_list: list[QwenSupportedModels] = []
        for model in response_data.data or []:
            try:
                model_enum = QwenSupportedModels(model.id)
            except ValueError:
                continue
            if model_enum in supported_models:
                models_list.append(model_enum)
        logger.debug(f"Received model list: {models_list}")
        return QwenModelsList(models=models_list)

    async def generate_completion(self, request: AnalyzeContentRequest) -> AnalyzeContentResponse:
        """Generate a completion using the Qwen API based on the given request."""
        logger.info(f"Generating completion with model: {request.model}")
        url = self.get_endpoint_url(QwenImplementedEndpoints.CHAT_COMPLETIONS)
        if isinstance(request.model, QwenSupportedModels):
            request_model = request.model
        elif isinstance(request.model, str):
            request_model = QwenSupportedModels(request.model)
        else:
            raise ValueError(
                f"Model '{request.model}' is not valid for the Qwen service. Use one of: {list(QwenSupportedModels)}"
            )
        request_body = QwenCompletionRequest(
            model=request_model,
            messages=[ChatMessage(role=ChatMessageRole.USER, content=request.prompt)],
        )
        response_data = QwenCompletionResponse.model_validate(await self._send_post_request(url, request_body))
        logger.debug("Generated chat completion successfully.")
        return AnalyzeContentResponse(response=response_data.choices[0].message.content)
