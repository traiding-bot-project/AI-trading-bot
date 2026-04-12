"""FastAPI router for handling User Service interactions."""

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, status
from src.db import get_user_services
from src.db.user_service import UserService
from src.models.fastapi.app import V1RouterTags
from src.models.user import User, UserFilters

logger = logging.getLogger(__name__)

user_router = APIRouter(prefix="/user", tags=[V1RouterTags.USER_SERVICE])


@user_router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    body: Annotated[User, Body(...)], user_service: Annotated[UserService, Depends(get_user_services)]
) -> Any:
    """Endpoint to register a new user."""
    logger.info("Registering new user")
    user = await user_service.register_user(body)
    return user


@user_router.get("/", response_model=list[User], status_code=status.HTTP_200_OK)
async def list_users(
    filters: Annotated[UserFilters, Depends()], user_service: Annotated[UserService, Depends(get_user_services)]
) -> Any:
    """Endpoint to list registered users."""
    logger.info("Listing all users")
    users = await user_service.list_users(filters)
    return users


@user_router.get("/{chat_id}", response_model=User, status_code=status.HTTP_200_OK)
async def get_user(chat_id: int, user_service: Annotated[UserService, Depends(get_user_services)]) -> Any:
    """Endpoint to retrieve a user by their Telegram chat ID."""
    logger.info(f"Retrieving user with chat_id {chat_id}")
    user = await user_service.get_user(chat_id)
    return user


@user_router.put("/", response_model=User, status_code=status.HTTP_200_OK)
async def update_user(
    body: Annotated[User, Body(...)], user_service: Annotated[UserService, Depends(get_user_services)]
) -> Any:
    """Endpoint to update an existing user."""
    logger.info("Updating user")
    user = await user_service.update_user(body)
    return user


@user_router.delete("/{chat_id}", response_model=User, status_code=status.HTTP_200_OK)
async def remove_user(chat_id: int, user_service: Annotated[UserService, Depends(get_user_services)]) -> Any:
    """Endpoint to remove a user."""
    logger.info(f"Removing user with chat_id {chat_id}")
    user = await user_service.remove_user(chat_id)
    return user
