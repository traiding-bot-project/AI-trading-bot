"""Create FastAPI server and mount MCP server."""

from fastapi import FastAPI
from src.router.api.api import api
from src.server.utils.mcp import create_sse_server
from src.router.mcp.mcp import mcp

app = FastAPI()
app.include_router(api)

app.mount("/mcp", create_sse_server(mcp))
