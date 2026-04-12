"""User Service for managing user operations in the Telegram User App Service."""

import logging

from src.db.protocol import UserRepository
from src.models.user import User, UserFilters

logger = logging.getLogger(__name__)


class UserService:
    """Provides high-level operations for managing users in the Telegram User App Service."""

    def __init__(self, repository: UserRepository) -> None:
        """Initialize UserService with a given UserRepository."""
        self._repo = repository
        logger.debug("UserService initialized with repository")

    async def register_user(self, user: User) -> User:
        """Register a new user in the system."""
        logger.info(f"Registering new user with chat_id {user.chat_id}")
        existing = await self._repo.get_user_by_chat_id(user.chat_id)
        if existing:
            logger.warning(f"User registration failed: user with chat_id {user.chat_id} already exists")
            raise ValueError(f"User with chat_id {user.chat_id} already exists")
        result = await self._repo.add_user(user)
        logger.info(f"User registered successfully with ID {result.id}")
        return result

    async def get_user(self, chat_id: int) -> User:
        """Retrieve a user by their Telegram chat ID."""
        logger.info(f"Retrieving user with chat_id {chat_id}")
        user = await self._repo.get_user_by_chat_id(chat_id)
        if not user:
            logger.warning(f"User not found: chat_id {chat_id}")
            raise ValueError(f"User with chat_id {chat_id} not found")
        logger.debug(f"Retrieved user: {user.username}")
        return user

    async def update_user(self, user: User) -> User:
        """Update an existing user's information."""
        logger.info(f"Updating user with chat_id {user.chat_id}")
        result = await self._repo.update_user(user)
        logger.debug(f"User updated successfully")
        return result

    async def list_users(self, filters: UserFilters) -> list[User]:
        """Retrieve a list of registered users with optional filtering."""
        logger.info(f"Listing users with filters: {filters.model_dump(exclude_none=True)}")
        users = await self._repo.get_all_users(filters)
        logger.debug(f"Retrieved {len(users)} users")
        return users

    async def remove_user(self, user_id: int) -> bool:
        """Delete a user by their ID."""
        logger.info(f"Removing user with ID {user_id}")
        success = await self._repo.delete_user(user_id)
        if success:
            logger.info(f"User deleted successfully")
        else:
            logger.warning(f"User deletion failed: user not found")
        return success
