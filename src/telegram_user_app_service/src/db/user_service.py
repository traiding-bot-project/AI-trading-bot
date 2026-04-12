"""Provides the UserService class for managing user operations in the Telegram User App Service."""

from src.db.protocol import UserRepository
from src.models.user import User, UserFilters


class UserService:
    """Provides high-level operations for managing users in the Telegram User App Service."""

    def __init__(self, repository: UserRepository) -> None:
        """Initializes the UserService with a given UserRepository."""
        self._repo = repository

    async def register_user(self, user: User) -> User:
        """Registers a new user. Raises ValueError if a user with the same chat_id already exists."""
        existing = await self._repo.get_user_by_chat_id(user.chat_id)
        if existing:
            raise ValueError(f"User with chat_id {user.chat_id} already exists")
        return await self._repo.add_user(user)

    async def get_user(self, chat_id: int) -> User:
        """Retrieves a user by their Telegram chat ID. Raises ValueError if the user is not found."""
        user = await self._repo.get_user_by_chat_id(chat_id)
        if not user:
            raise ValueError(f"User with chat_id {chat_id} not found")
        return user

    async def update_user(self, user: User) -> User:
        """Updates an existing user. Raises ValueError if the user is not found."""
        return await self._repo.update_user(user)

    async def list_users(self, filters: UserFilters) -> list[User]:
        """Returns a list of registered users."""
        return await self._repo.get_all_users(filters)

    async def remove_user(self, user_id: int) -> bool:
        """Deletes a user by their ID. Returns True if deletion was successful, False otherwise."""
        return await self._repo.delete_user(user_id)
