"""AI service implementations."""

from src.interfaces.ai_service import AIService
from src.services.ollama import OllamaService
from src.services.qwen import QwenService
from src.settings import settings


def get_ai_service() -> AIService:
    """Factory function to get the appropriate AI service implementation based on settings."""
    providers = {"ollama": OllamaService(), "qwen": QwenService()}
    active_deployment_key = settings.ai_model.active_deployment
    deployment_config = getattr(settings.ai_model.deployments, active_deployment_key)
    compatible_api = deployment_config.api.compatible_api

    if compatible_api not in providers:
        raise ValueError(f"Unsupported compatible API provider: {compatible_api}")
    return providers[compatible_api]
