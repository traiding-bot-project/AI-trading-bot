"""FastAPI application and API router definitions for the News Analysis Service."""

import logging
from typing import Any

from fastapi import APIRouter, FastAPI, status
from src.fastapi.ollama import ollama_router
from src.models.fastapi.app import HealthCheck

logger = logging.getLogger(__name__)
logger.info("Initializing News Analysis Service FastAPI application")

app = FastAPI(
    title="News Analysis Service", description="Microservice for analyzing news content using AI", version="1.0.0"
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
