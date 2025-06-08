from fastapi import APIRouter

from src.routers.v1.v1 import v1

api = APIRouter(
    prefix="/api",
    responses={404: {"description": "Not found"}}
)

api.include_router(v1)
