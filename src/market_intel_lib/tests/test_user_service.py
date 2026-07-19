"""Tests for ``market_intel_lib.db.users.user_service``.

Locks down the guard logic in ``UserService`` (duplicate registration, missing
lookups, deletion result pass-through) against an in-memory fake repository.
"""

import asyncio

import pytest

from market_intel_lib.db.users.user_service import UserService
from market_intel_lib.models.user import User


class FakeUserRepository:
    """In-memory stand-in for ``UserRepository`` covering the methods UserService uses."""

    def __init__(
        self,
        *,
        existing_user: User | None = None,
        delete_result: bool = True,
    ) -> None:
        """Configure the user returned by lookups and the delete_user return value."""
        self._existing_user = existing_user
        self._delete_result = delete_result
        self.added_user: User | None = None
        self.deleted_user_id: int | None = None

    async def get_user_by_chat_id(self, chat_id: int) -> User | None:
        """Return the preconfigured user regardless of the requested chat_id."""
        return self._existing_user

    async def add_user(self, user: User) -> User:
        """Record the user and echo it back with an assigned id."""
        self.added_user = user
        return user.model_copy(update={"id": 1})

    async def delete_user(self, user_id: int) -> bool:
        """Record the id and return the preconfigured deletion result."""
        self.deleted_user_id = user_id
        return self._delete_result


def _make_user(*, chat_id: int = 99) -> User:
    """Build a valid user with the given chat_id."""
    return User(
        first_name="Ada",
        last_name="Lovelace",
        username="ada",
        chat_id=chat_id,
    )


def test_register_user_returns_added_user_when_new() -> None:
    """Registering an unknown chat_id delegates to add_user and returns the result."""
    repo = FakeUserRepository(existing_user=None)
    service = UserService(repo)
    user = _make_user()

    result = asyncio.run(service.register_user(user))

    assert result.id == 1
    assert repo.added_user is user


def test_register_user_raises_when_chat_id_exists() -> None:
    """Registering a chat_id that already exists raises ValueError and skips add_user."""
    existing = _make_user()
    repo = FakeUserRepository(existing_user=existing)
    service = UserService(repo)

    with pytest.raises(ValueError, match="already exists"):
        asyncio.run(service.register_user(_make_user()))

    assert repo.added_user is None


def test_get_user_returns_user_when_found() -> None:
    """get_user returns the user served by the repository."""
    existing = _make_user()
    service = UserService(FakeUserRepository(existing_user=existing))

    result = asyncio.run(service.get_user(99))

    assert result is existing


def test_get_user_raises_when_not_found() -> None:
    """get_user raises ValueError when the repository has no matching user."""
    service = UserService(FakeUserRepository(existing_user=None))

    with pytest.raises(ValueError, match="not found"):
        asyncio.run(service.get_user(99))


def test_remove_user_passes_through_true() -> None:
    """remove_user returns the repository's True result and forwards the id."""
    repo = FakeUserRepository(delete_result=True)
    service = UserService(repo)

    assert asyncio.run(service.remove_user(7)) is True
    assert repo.deleted_user_id == 7


def test_remove_user_passes_through_false() -> None:
    """remove_user returns the repository's False result when nothing was deleted."""
    service = UserService(FakeUserRepository(delete_result=False))

    assert asyncio.run(service.remove_user(7)) is False
