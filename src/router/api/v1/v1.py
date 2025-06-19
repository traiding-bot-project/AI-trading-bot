"""API v1 versioning definition."""

from fastapi import APIRouter

v1 = APIRouter(prefix="/v1", responses={404: {"description": "Not found"}})

@v1.get("/")
def index() -> dict[str, str]:
    """Example FastAPI endpoint."""
    return {"message": "kekus"}
