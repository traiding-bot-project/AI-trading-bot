"""AI service implementations."""

from src.interfaces.ai_service import AIService
from src.services.ollama import OllamaService
from src.settings import settings


def get_ai_service() -> AIService:
    """Factory function to get the appropriate AI service implementation based on settings."""
    providers = {
        "ollama": OllamaService(),
    }
    compatible_api = settings.ai_model.deployments.ollama_deployments.api.compatible_api
    if compatible_api not in providers:
        raise ValueError(f"Unsupported compatible API provider: {compatible_api}")
    return providers[compatible_api]
