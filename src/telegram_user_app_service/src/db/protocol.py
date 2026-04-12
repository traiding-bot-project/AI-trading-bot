"""Defines the UserRepository protocol for the Telegram User App Service."""

from typing import Protocol

from src.models.user import User, UserFilters


class UserRepository(Protocol):
    """Defines the UserRepository protocol for managing user data in the Telegram User App Service."""

    async def add_user(self, user: User) -> User:
        """Adds a new user to the repository and returns the created User object."""
        ...

    async def get_user_by_chat_id(self, chat_id: int) -> User | None:
        """Retrieves a user by their Telegram chat ID. Returns None if the user is not found."""
        ...

    async def get_all_users(self, filters: UserFilters) -> list[User]:
        """Returns a list of users in the repository."""
        ...

    async def update_user(self, user: User) -> User:
        """Updates an existing user in the repository and returns the updated User object."""
        ...

    async def delete_user(self, user_id: int) -> bool:
        """Deletes a user by their ID. Returns True if deletion was successful, False otherwise."""
        ...
