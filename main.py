from fastapi import FastAPI

from src.routers.api import api

app = FastAPI()

app.include_router(api)
