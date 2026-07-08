"""Interface definitions for AI service interactions."""

from src.analyzer.content_analyzer import AIContentAnalyzer
from src.services import get_ai_service
from src.settings import settings
from src.settings.models.settings_model import (
    CompatibleAPI,
    OllamaSupportedModels,
    QwenSupportedModels,
)


def get_content_analyzer(api_name: CompatibleAPI) -> AIContentAnalyzer:
    """Create a new content analyzer for the requested AI service provider."""
    return AIContentAnalyzer(get_ai_service(api_name))


def get_compatible_api_for_model(
    model_name: OllamaSupportedModels | QwenSupportedModels,
) -> CompatibleAPI:
    """Return the compatible API provider name for the requested model."""
    deployments = settings.ai_model.deployments
    models_to_api = [(deployment.api.compatible_api, deployment.models) for _, deployment in deployments]
    for api, models in models_to_api:
        if model_name in models:
            return CompatibleAPI(api)
    raise ValueError(f"Model '{model_name}' is not supported by any configured API provider.")


__all__ = ["get_content_analyzer", "get_compatible_api_for_model"]
