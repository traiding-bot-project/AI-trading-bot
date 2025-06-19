"""Entrypoint to the program."""

from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

from src.router.api import api
from src.mcp.mcp import mcp

app = FastAPI()
app.include_router(api)
app.include_router(mcp)

mcp_server = FastApiMCP(app)

mcp_server.mount(mcp)

