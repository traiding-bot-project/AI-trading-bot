"""Secrets management for the Telegram user application."""

from logging import getLogger

from src.secrets.infisical import InfisicalSecretsManager
from src.secrets.protocol import SecretsManager
from src.settings import settings

logger = getLogger(__name__)

secrets_manager: SecretsManager = InfisicalSecretsManager(settings.infisical)
logger.info("Secrets manager initialized successfully.")

__all__ = [
    "secrets_manager",
]
