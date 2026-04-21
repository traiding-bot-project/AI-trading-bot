"""Infisical models."""

from enum import StrEnum


class InfisicalSecretsKeys(StrEnum):
    """Enum for Infisical secrets used in the application."""

    TELEGRAM_ACCESS_TOKEN = "TELEGRAM_ACCESS_TOKEN"
    DB_PASSWORD = "DB_PASSWORD"
