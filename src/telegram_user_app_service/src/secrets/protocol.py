"""Secrets management protocol."""

from typing import Protocol

from src.models.infisical import InfisicalSecretsKeys


class SecretsManager(Protocol):
    """Protocol for secrets management. Defines the expected interface for retrieving secrets."""

    def get_secret(self, secret_name: InfisicalSecretsKeys) -> str:
        """Retrieve the value of a secret by its name."""
        ...
