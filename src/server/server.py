"""Create FastAPI server and mount MCP server."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.router.api.api import api
from src.router.mcp.mcp import mcp


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan to initiate MCP server before mounting on FastAPI."""
    await mcp.run_streamable_http_async()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(api)

app.mount("/", mcp.streamable_http_app())
