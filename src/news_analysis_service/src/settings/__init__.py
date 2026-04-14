"""Settings module for the Sentiment Analysis Service microservice."""

from logging import getLogger

from src.constants import SETTINGS_PATH
from src.settings.models.settings_model import Settings
from src.utils.ingest_toml import load_settings

logger = getLogger(__name__)

settings = load_settings(SETTINGS_PATH, Settings)
logger.info("Created general settings from configuration file")

__all__ = ["settings"]
