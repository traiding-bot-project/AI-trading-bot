"""FastAPI router for handling Telegram bot interactions."""

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, status
from src.models.bot import BroadcastResponse
from src.models.fastapi.app import V1RouterTags
from src.models.structured_input import NewsItem
from src.telegram.bot import get_broadcast_bot
from src.telegram.bot.telegram_bot import BroadcastBot

logger = logging.getLogger(__name__)

bot_router = APIRouter(prefix="/bot", tags=[V1RouterTags.TELEGRAM_BOT])


@bot_router.post(
    "/broadcast", response_model=BroadcastResponse, status_code=status.HTTP_200_OK
)
async def broadcast(
    body: Annotated[NewsItem | str, Body(...)],
    bot: Annotated[BroadcastBot, Depends(get_broadcast_bot)],
) -> Any:
    """Endpoint to broadcast a message to all subscribed Telegram users."""
    logger.info("POST /bot/broadcast - Broadcasting message to all subscribed users")
    logger.debug(f"Message to broadcast: {body}")
    await bot.broadcast(body)
    logger.info("Broadcast completed successfully")
    return BroadcastResponse(success=True)
