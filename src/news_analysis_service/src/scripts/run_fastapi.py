"""Script to run the FastAPI application."""

from logging import getLogger

from uvicorn import run

from src.constants import FASTAPI_SETTINGS_PATH
from src.settings import settings
from src.settings.models.fastapi_settings_model import FastAPISettings
from src.utils.ingest_toml import load_settings
from src.utils.logger import configure_logging

logger = getLogger(__name__)


def main() -> None:
    """Main function to run the FastAPI application."""
    configure_logging(settings.service.logging_level)
    fastapi_settings = load_settings(FASTAPI_SETTINGS_PATH, FastAPISettings)
    logger.info("Created FastAPI settings from configuration file")
    logger.info(f"Starting FastAPI server on {fastapi_settings.host}:{fastapi_settings.port}")

    from src.fastapi.app import app

    run(
        app,
        host=fastapi_settings.host,
        port=fastapi_settings.port,
        log_level=settings.service.logging_level,
        reload=False,
    )


if __name__ == "__main__":
    main()
