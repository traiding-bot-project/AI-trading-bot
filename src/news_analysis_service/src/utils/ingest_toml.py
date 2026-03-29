"""Utility functions for loading settings from a TOML file."""

from pathlib import Path
from tomllib import load


def load_settings[T](config_path: str | Path, settings_model: type[T]) -> T:
    """Load settings from a TOML file and return a Settings instance."""
    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Settings file not found: {config_path}")

    with open(config_path, "rb") as f:
        config_data = load(f)

    settings = settings_model(**config_data)
    return settings
