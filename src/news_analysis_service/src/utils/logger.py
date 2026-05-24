"""Logging configuration for the News Analysis Service."""

import logging

from src.settings.models.settings_model import LoggingLevel


def configure_logging(level: LoggingLevel) -> None:
    """Configure the root logger with the specified logging level and console output."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    logger = logging.getLogger()
    logger.setLevel(numeric_level)

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
