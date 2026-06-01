"""Secrets management protocol."""

from enum import StrEnum
from typing import Protocol


class SecretsManager(Protocol):
    """Protocol for secrets management. Defines the expected interface for retrieving secrets."""

    def get_secret(self, secret_name: InfisicalSecretsKeys) -> str:
        """Retrieve the value of a secret by its name."""
        ...
