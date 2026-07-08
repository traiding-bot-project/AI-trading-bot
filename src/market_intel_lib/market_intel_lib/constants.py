"""Constants for the market intel package."""

from pathlib import Path
import market_intel_lib

lib_root = Path(market_intel_lib.__file__).parent.parent
SETTINGS_PATH = lib_root / "market_intel_lib" / "settings" / "settings.toml"

SUBSCRIPTION_TOKEN_EXPIRATION_SECONDS = 60 * 60 * 24
