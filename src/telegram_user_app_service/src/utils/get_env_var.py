"""Utility functions for retrieving and validating environment variables."""

import logging
import os

logger = logging.getLogger(__name__)


def get_env_var(var_name: str) -> str:
    """Retrieve an environment variable by its name. Raises an error if the variable is not set."""
    logger.debug(f"Retrieving environment variable: {var_name}")
    var = os.getenv(var_name)
    if var is None:
        logger.error(f"Environment variable '{var_name}' is not set")
        raise OSError(f"Environment variable '{var_name}' is not set.")
    logger.debug(f"Successfully retrieved environment variable: {var_name}")
    return var
