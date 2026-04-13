"""FastAPI router for handling User Service interactions."""

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, status
from pydantic import Field
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
    """Endpoint to register a new Telegram user."""
    logger.info(f"POST /user - Registering new user with chat_id {body.chat_id}")
    logger.debug(f"User details - username: {body.username}, first_name: {body.first_name}")
    user = await user_service.register_user(body)
    logger.info(f"User registered successfully with ID {user.id}")
    return user


@user_router.get("/", response_model=list[User], status_code=status.HTTP_200_OK)
async def list_users(
    filters: Annotated[UserFilters, Depends()], user_service: Annotated[UserService, Depends(get_user_services)]
) -> Any:
    """Endpoint to list registered Telegram users with optional filtering."""
    logger.info("GET /user - Listing users")
    logger.debug(f"Applied filters: subscribed={filters.is_subscribed}")
    users = await user_service.list_users(filters)
    logger.debug(f"Retrieved {len(users)} users")
    return users


@user_router.get("/{chat_id}", response_model=User, status_code=status.HTTP_200_OK)
async def get_user(chat_id: Annotated[int, Field(gt=0)], user_service: Annotated[UserService, Depends(get_user_services)]) -> Any:
    """Endpoint to retrieve a user by their Telegram chat ID."""
    logger.info(f"GET /user/{{{chat_id}}} - Retrieving user with chat_id {chat_id}")
    user = await user_service.get_user(chat_id)
    logger.debug(f"Retrieved user: {user.username}")
    return user


@user_router.put("/", response_model=User, status_code=status.HTTP_200_OK)
async def update_user(
    body: Annotated[User, Body(...)], user_service: Annotated[UserService, Depends(get_user_services)]
) -> Any:
    """Endpoint to update an existing user's information."""
    logger.info(f"PUT /user - Updating user with chat_id {body.chat_id}")
    logger.debug(f"Update payload: username={body.username}, subscribed={body.is_subscribed}")
    user = await user_service.update_user(body)
    logger.info("User updated successfully")
    return user


@user_router.delete("/{chat_id}", response_model=User, status_code=status.HTTP_200_OK)
async def remove_user(chat_id: Annotated[int, Field(gt=0)], user_service: Annotated[UserService, Depends(get_user_services)]) -> Any:
    """Endpoint to remove a user by their Telegram chat ID."""
    logger.info(f"DELETE /user/{{{chat_id}}} - Removing user with chat_id {chat_id}")
    user = await user_service.remove_user(chat_id)
    logger.info("User removed successfully")
    return user
