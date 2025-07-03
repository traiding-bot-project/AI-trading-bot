"""Custom logger."""

import logging

from src.utils.formatter import Formatter


def get_custom_logger(
    name: str,
    server_tag: str = "GENERIC",
) -> logging.Logger:
    """Create custom logger."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(Formatter())

        logger.addHandler(console_handler)

    class ServerContextFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            record.server = server_tag
            return True

    logger.filters.clear()
    logger.addFilter(ServerContextFilter())

    return logger
