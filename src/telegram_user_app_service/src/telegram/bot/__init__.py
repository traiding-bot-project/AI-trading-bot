"""Telegram bot implementation."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from src.db import user_service_context
from src.telegram.bot.telegram_bot import BroadcastBot


@asynccontextmanager
async def broadcast_bot_context() -> AsyncGenerator[BroadcastBot]:
    """Context manager for use outside FastAPI."""
    async with user_service_context() as user_service:
        yield BroadcastBot(user_service)


async def get_broadcast_bot() -> AsyncGenerator[BroadcastBot]:
    """Factory function to create a BroadcastBot instance."""
    async with broadcast_bot_context() as bot:
        yield bot


__all__ = ["get_broadcast_bot", "broadcast_bot_context"]
