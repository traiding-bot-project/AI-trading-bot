"""API v1 versioning definition."""

from fastapi import APIRouter

from src.router.v1.alpaca_trading import alpaca_trading

v1 = APIRouter(prefix="/v1", responses={404: {"description": "Not found"}})

v1.include_router(alpaca_trading)
