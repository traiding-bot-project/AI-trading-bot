"""v1 API route definition."""

from fastapi import APIRouter
from src.fastapi.v1.ollama import ollama_router

v1 = APIRouter(prefix="/v1")

v1.include_router(ollama_router)
