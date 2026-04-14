"""FastAPI application and API router definitions for the Telegram User App Service."""

import logging
import threading
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import APIRouter, FastAPI, status
from src.fastapi.telegram_bot import bot_router
from src.fastapi.user_service import user_router
from src.models.fastapi.app import HealthCheck
from src.telegram.app import start_telegram_application

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Lifespan context manager to start the Telegram bot in a background thread."""
    logger.info("Starting Telegram bot in background thread...")
    telegram_thread = threading.Thread(target=start_telegram_application, daemon=True)
    telegram_thread.start()
    logger.info("Telegram bot background thread started successfully")
    yield
    logger.info("FastAPI application shutting down")


app = FastAPI(
    lifespan=lifespan,
    title="Telegram User App Service",
    description="Microservice for Telegram user management and notifications",
    version="1.0.0",
)
logger.info("FastAPI application instance created with lifespan context manager")


@app.get("/health", status_code=status.HTTP_200_OK, response_model=HealthCheck)
def get_health() -> Any:
    """Endpoint for checking if the FastAPI server is running."""
    logger.debug("Health check called")
    return HealthCheck()


api = APIRouter(prefix="/api")

api.include_router(bot_router)
api.include_router(user_router)

app.include_router(api)
