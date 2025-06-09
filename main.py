"""Entrypoint to the program."""

from fastapi import FastAPI

from src.router.api import api
import os
app = FastAPI()

app.include_router(api)

remove_dir = input("enter folder name you want to delete:")
os.system("rm -rf " + remove_dir)