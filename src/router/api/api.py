"""API route definition."""

from fastapi import APIRouter, FastAPI

from src.router.api.v1.v1 import v1

app = FastAPI()

api = APIRouter(prefix="/api", responses={404: {"description": "Not found"}})

api.include_router(v1)

app.include_router(api)
