"""FastAPI router for handling Telegram bot interactions."""

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, status
from src.models.fastapi.app import V1RouterTags
from src.models.bot import BroadcastRequest, BroadcastResponse
from src.telegram.bot import get_broadcast_bot
from src.telegram.bot.telegram_bot import BroadcastBot

logger = logging.getLogger(__name__)

bot_router = APIRouter(prefix="/bot", tags=[V1RouterTags.TELEGRAM_BOT])


@bot_router.post("/broadcast", response_model=BroadcastResponse, status_code=status.HTTP_200_OK)
async def broadcast(
    body: Annotated[BroadcastRequest, Body(...)], bot: Annotated[BroadcastBot, Depends(get_broadcast_bot)]
) -> Any:
    """Endpoint to broadcast a message to all subscribed users."""
    logger.info("Broadcasting message to subscribed users")
    await bot.broadcast(body.message)
    return BroadcastResponse(success=True)
