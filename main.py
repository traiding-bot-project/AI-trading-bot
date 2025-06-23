"""Entrypoint to the program."""

import asyncio
import os

import uvicorn

from src.router.api.api import app
from src.router.mcp.mcp import mcp

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
MCP_PORT = int(os.getenv("MCP_PORT", "8001"))


async def run_servers() -> None:
    """Run both FastAPI and MCP servers concurrently."""
    fastapi_config = uvicorn.Config(app, host=HOST, port=PORT)
    fastapi_server = uvicorn.Server(fastapi_config)

    mcp_config = uvicorn.Config(mcp.streamable_http_app(), host=HOST, port=MCP_PORT)
    mcp_server = uvicorn.Server(mcp_config)

    await asyncio.gather(fastapi_server.serve(), mcp_server.serve())


def run() -> None:
    """Start the FastAPI server with uvicorn."""
    asyncio.run(run_servers())


if __name__ == "__main__":
    run()
