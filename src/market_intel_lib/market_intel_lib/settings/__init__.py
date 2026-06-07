"""Settings module for the Telegram User App Service microservice."""

from market_intel_lib.constants import SETTINGS_PATH
from market_intel_lib.models.settings import Settings
from market_intel_lib.toml.ingest_toml import load_settings

settings = load_settings(SETTINGS_PATH, Settings)

__all__ = ["settings"]
