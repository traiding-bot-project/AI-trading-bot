"""Protocol definitions for user repository interactions."""

from typing import Protocol

from src.models.user import User, UserFilters


class UserRepository(Protocol):
    """Protocol defining the interface for user repository operations."""

    async def add_user(self, user: User) -> User:
        """Add a new user to the repository and return the created User object."""
        ...

    async def get_user_by_chat_id(self, chat_id: int) -> User | None:
        """Retrieve a user by their Telegram chat ID."""
        ...

    async def get_all_users(self, filters: UserFilters) -> list[User]:
        """Retrieve all users from the repository, optionally filtered."""
        ...

    async def update_user(self, user: User) -> User:
        """Update an existing user in the repository and return the updated User object."""
        ...

    async def delete_user(self, user_id: int) -> bool:
        """Delete a user by their ID."""
        ...
