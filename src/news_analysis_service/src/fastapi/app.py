"""API route definition."""

import logging
from typing import Any

from fastapi import APIRouter, FastAPI, status
from src.fastapi.v1.v1 import v1
from src.models.fastapi.app import HealthCheck

logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/health", status_code=status.HTTP_200_OK, response_model=HealthCheck)
def get_health() -> Any:
    """Endpoint for checking if FastAPI server runs."""
    logger.info("Health check called")
    return HealthCheck()


api = APIRouter(prefix="/api")

api.include_router(v1)

app.include_router(api)
