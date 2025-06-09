"""Entrypoint to the program."""

from fastapi import FastAPI

from src.router.api import api

app = FastAPI()

app.include_router(api)
