"""E2E tests for the app."""

import socket
import subprocess
import time

import httpx
import pytest
from fastapi import status

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.types import (
    ListPromptsResult,
    ListResourcesResult,
    ListResourceTemplatesResult,
    ListToolsResult,
)

HOST = "127.0.0.1"
PORT = 8000
MCP_PORT = 8001


def create_request_link(host: str = HOST, port: int = PORT, endpoint: str = "/") -> str:
    """Request link builder."""
    return f"http://{host}:{port}{endpoint}"


def wait_for_port(host: str, port: int, timeout: float = 10.0) -> bool | None:
    """Wait until a TCP port is open and server is up."""
    start = time.time()
    while time.time() - start < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.connect((host, port))
                return True
            except ConnectionRefusedError:
                time.sleep(0.2)
    raise TimeoutError(f"Port {port} on {host} did not open in time.")


@pytest.fixture(scope="session", autouse=True)
def run_servers():
    """Start both FastAPI and MCP servers in a subprocess."""
    server = subprocess.Popen(["python", "main.py"])
    try:
        wait_for_port(HOST, PORT)
        wait_for_port(HOST, MCP_PORT)
        yield
    finally:
        server.terminate()
        server.wait()


@pytest.mark.asyncio
async def test_fastapi_server_runs():
    """Test if FastAPI server works."""
    async with httpx.AsyncClient() as client:
        response = await client.get(create_request_link(endpoint="/health"))
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "OK"}


@pytest.mark.asyncio
async def test_mcp_server_runs():
    """Test if MCP server works."""
    async with streamablehttp_client(
        create_request_link(port=MCP_PORT, endpoint="/mcp")
    ) as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            assert isinstance(await session.list_tools(), ListToolsResult)
            assert isinstance(await session.list_prompts(), ListPromptsResult)
            assert isinstance(
                await session.list_resource_templates(), ListResourceTemplatesResult
            )
            assert isinstance(await session.list_resources(), ListResourcesResult)
