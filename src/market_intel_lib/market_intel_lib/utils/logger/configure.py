"""Logging configuration for the Telegram User App Service."""

from enum import StrEnum
import logging


class LoggingLevel(StrEnum):
    """Logging levels for the service.

    Can be used to configure the logging level of the application based on the deployment or environment.
    """

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


def configure_logging(level: LoggingLevel) -> None:
    """Configure the root logger with the specified level and console output."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    logger = logging.getLogger()
    logger.setLevel(numeric_level)

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
