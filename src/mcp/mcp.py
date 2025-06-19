"""API route definition."""

from fastapi import APIRouter

from src.mcp.v1.v1 import v1

mcp = APIRouter(prefix="/mcp", responses={404: {"description": "Not found"}})

mcp.include_router(v1)