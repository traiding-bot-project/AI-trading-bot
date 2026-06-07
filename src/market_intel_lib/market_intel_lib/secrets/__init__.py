"""Secrets management for the Telegram user application."""

from logging import getLogger

from market_intel_lib.secrets.infisical import InfisicalSecretsManager
from market_intel_lib.secrets.protocol import SecretsManager
from market_intel_lib.settings import settings

logger = getLogger(__name__)

secrets_manager: SecretsManager = InfisicalSecretsManager(settings.infisical)
logger.info("Secrets manager initialized successfully.")

__all__ = [
    "secrets_manager",
]
