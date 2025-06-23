"""Entrypoint to the program."""

import os

import uvicorn

from src.server.server import app

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))


def run() -> None:
    """Start the FastAPI server with uvicorn."""
    uvicorn.run(app, host=HOST, port=PORT)


if __name__ == "__main__":
    run()
