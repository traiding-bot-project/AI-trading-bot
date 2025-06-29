"""API route definition."""

from typing import Any

from fastapi import APIRouter, FastAPI, status

from src.router.api.v1.v1 import v1
from src.router.types.api import HealthCheck

app = FastAPI()


@app.get("/health", status_code=status.HTTP_200_OK, response_model=HealthCheck)
def get_health() -> Any:
    """Endpoint for checking if FastAPI server runs."""
    return HealthCheck()


api = APIRouter(prefix="/api", responses={404: {"description": "Not found"}})

api.include_router(v1)

app.include_router(api)
