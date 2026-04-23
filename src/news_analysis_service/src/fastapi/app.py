"""FastAPI application and API router definitions for the News Analysis Service."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import APIRouter, FastAPI, status
from src.fastapi.ollama import ollama_router
from src.interfaces import content_analyzer
from src.models.fastapi.app import HealthCheck

logger = logging.getLogger(__name__)
logger.info("Initializing News Analysis Service FastAPI application")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Lifespan context manager for FastAPI application to perform startup and shutdown tasks."""
    await content_analyzer.log_available_models()
    yield


app = FastAPI(
    title="News Analysis Service",
    description="Microservice for analyzing news content using AI",
    version="1.0.0",
    lifespan=lifespan,
)
logger.info("FastAPI application instance created")


@app.get("/health", status_code=status.HTTP_200_OK, response_model=HealthCheck)
def get_health() -> Any:
    """Endpoint for checking if the FastAPI server is running."""
    logger.debug("Health check endpoint is called")
    return HealthCheck()


api = APIRouter(prefix="/api")

api.include_router(ollama_router)

app.include_router(api)
