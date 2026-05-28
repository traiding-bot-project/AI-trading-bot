"""AI service implementations."""

from typing import cast

from src.analyzer.ai_service import AIService
from src.services.ollama import OllamaService
from src.services.qwen import QwenService
from src.settings import settings
from src.settings.models.settings_model import CompatibleAPI


def get_ai_service(api_name: CompatibleAPI) -> AIService:
    """Factory function to get the appropriate AI service implementation based on settings."""
    providers = {
        CompatibleAPI.OLLAMA: OllamaService(),
        CompatibleAPI.QWEN: QwenService(),
    }

    compatible_apis = {deployment.api.compatible_api for _, deployment in settings.ai_model.deployments}

    if api_name not in compatible_apis:
        raise ValueError(f"Unsupported compatible API provider: {api_name}")
    return cast(AIService, providers[api_name])
