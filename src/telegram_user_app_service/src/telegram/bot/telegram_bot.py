"""Bot implementation for broadcasting messages to subscribed users."""

import logging

from market_intel_lib.db.users.user_service import UserService
from market_intel_lib.models.infisical import InfisicalSecretsKeys
from market_intel_lib.secrets import secrets_manager
from market_intel_lib.models.user import UserFilters
from src.models.structured_input import NewsItem, StructuredOutputResponse
from telegram import Bot, LinkPreviewOptions
from telegram.constants import ParseMode

logger = logging.getLogger(__name__)


class BroadcastBot:
    """A Telegram bot that broadcasts messages to subscribed users."""

    def __init__(self, user_service: UserService) -> None:
        """Initialize the BroadcastBot with the given UserService."""
        token = secrets_manager.get_secret(InfisicalSecretsKeys.TELEGRAM_ACCESS_TOKEN)
        self._bot = Bot(token=token)
        self._user_service = user_service

    async def broadcast(self, message: NewsItem | str) -> None:
        """Broadcast a message to all subscribed users."""
        subscribed_users = await self._user_service.list_users(
            filters=UserFilters(is_subscribed=True)
        )

        if not subscribed_users:
            logger.info("No subscribed users to broadcast to.")
            return

        logger.info(f"Broadcasting to {len(subscribed_users)} subscribed user(s).")
        for user in subscribed_users:
            if isinstance(message, NewsItem):
                formatted_message = self._format_message(message)
            else:
                formatted_message = message
            await self._send(user.chat_id, formatted_message)

    async def _send(self, chat_id: int, message: str) -> None:
        """Send a message to a single user, logging success or failure."""
        try:
            await self._bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=ParseMode.HTML,
                link_preview_options=LinkPreviewOptions(is_disabled=True),
            )
            logger.info(f"Message sent to user {chat_id}.")
        except Exception as e:
            logger.error(f"Failed to send message to user {chat_id}: {e}")

    def _format_message(self, news_item: NewsItem) -> str:
        """Format a NewsItem into a string message for broadcasting."""
        assert isinstance(news_item.response, StructuredOutputResponse), (
            "Response must be parsed before formatting"
        )

        first_line = (
            f'<b><a href="{news_item.link}">{news_item.response.title}</a></b>\n'
        )
        second_line = (
            f"🌐 {news_item.response.source} | 📅 {news_item.response.published_at}\n\n"
        )
        summary = f"🔍 Summary\n{news_item.response.summary}\n\n"
        market_takeaways = "\n".join(
            [
                f"📌 {takeaway.sector}: {takeaway.sentiment} - {takeaway.impact}"
                for takeaway in news_item.response.market_takeaways
            ]
        )
        return (
            f"{first_line}{second_line}{summary}💲 Market Takeaways\n{market_takeaways}"
        )

    async def close(self) -> None:
        """Clean up resources."""
        await self._bot.close()
