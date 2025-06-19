"""Entrypoint to the program."""

from src.server.server import app
import uvicorn
import os


HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))


def run():
    """Start the FastAPI server with uvicorn."""
    uvicorn.run(app, host=HOST, port=PORT)


if __name__ == "__main__":
    run()
