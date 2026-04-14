"""Module for Telegram app handlers."""

from enum import StrEnum


class TelegramAppHandlers(StrEnum):
    """Enum for Telegram app handlers."""

    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
