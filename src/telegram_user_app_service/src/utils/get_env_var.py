"""Utility function to retrieve environment variables with error handling."""

import os


def get_env_var(var_name: str) -> str:
    """Retrieve an environment variable by its name. Raises an error if the variable is not set."""
    var = os.getenv(var_name)
    if var is None:
        raise OSError(f"Environment variable '{var_name}' is not set and no default value provided.")
    return var
