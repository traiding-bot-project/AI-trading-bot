"""Bot implementation for broadcasting messages to subscribed users."""

import logging

from src.db.user_service import UserService
from src.models.infisical import InfisicalSecretsKeys
from src.models.user import UserFilters
from src.secrets import secrets_manager
from telegram import Bot

logger = logging.getLogger(__name__)


class BroadcastBot:
    """A Telegram bot that broadcasts messages to subscribed users."""

    def __init__(self, user_service: UserService) -> None:
        """Initialize the BroadcastBot with the given UserService."""
        token = secrets_manager.get_secret(InfisicalSecretsKeys.TELEGRAM_ACCESS_TOKEN)
        self._bot = Bot(token=token)
        self._user_service = user_service

    async def broadcast(self, message: str) -> None:
        """Broadcast a message to all subscribed users."""
        subscribed_users = await self._user_service.list_users(filters=UserFilters(is_subscribed=True))

        if not subscribed_users:
            logger.info("No subscribed users to broadcast to.")
            return

        logger.info(f"Broadcasting to {len(subscribed_users)} subscribed user(s).")
        for user in subscribed_users:
            await self._send(user.chat_id, message)

    async def _send(self, chat_id: int, message: str) -> None:
        try:
            await self._bot.send_message(chat_id=chat_id, text=message)
            logger.info(f"Message sent to user {chat_id}.")
        except Exception as e:
            logger.error(f"Failed to send message to user {chat_id}: {e}")

    async def close(self) -> None:
        """Clean up resources."""
        await self._bot.close()
