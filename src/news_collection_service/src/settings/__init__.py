"""Settings module for the News Collection microservice."""

from logging import getLogger

from market_intel_lib.utils.toml.ingest_toml import load_settings

from src.constants import SETTINGS_PATH
from src.settings.models.settings_model import Settings

logger = getLogger(__name__)

settings = load_settings(SETTINGS_PATH, Settings)
logger.info("Created general settings from configuration file")

__all__ = ["settings"]
