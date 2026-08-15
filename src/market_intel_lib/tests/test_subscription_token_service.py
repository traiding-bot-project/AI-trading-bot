"""Tests for ``market_intel_lib.db.subscriptions.subscription_token_service``.

Exercises the token lifecycle business logic (creation, validation, activation)
against an in-memory fake repository, so no database is required.
"""

import asyncio
from datetime import UTC, datetime, timedelta

import pytest

from market_intel_lib.db.subscriptions.subscription_token_service import (
    SubscriptionTokenService,
)
from market_intel_lib.models.subscription_token import SubscriptionToken
from market_intel_lib.models.user import User


class FakeSubscriptionTokenRepository:
    """In-memory stand-in for ``SubscriptionTokenRepository``.

    Echoes tokens back on write and serves a preconfigured token on lookup,
    while recording the arguments it was called with for assertions.
    """

    def __init__(self, token_by_value: SubscriptionToken | None = None) -> None:
        """Configure the token returned by ``get_token_by_value`` (or None)."""
        self._token_by_value = token_by_value
        self.created_token: SubscriptionToken | None = None
        self.updated_token: SubscriptionToken | None = None

    async def create_token(self, token: SubscriptionToken) -> SubscriptionToken:
        """Record and echo back the created token."""
        self.created_token = token
        return token

    async def get_token_by_value(self, token_value: str) -> SubscriptionToken | None:
        """Return the preconfigured token regardless of the requested value."""
        return self._token_by_value

    async def update_token(self, token: SubscriptionToken) -> SubscriptionToken:
        """Record and echo back the updated token."""
        self.updated_token = token
        return token

    async def list_tokens(self) -> list[SubscriptionToken]:
        """Not exercised by these tests."""
        raise NotImplementedError

    async def list_tokens_by_username(self, username: str) -> list[SubscriptionToken]:
        """Not exercised by these tests."""
        raise NotImplementedError


def _make_token(
    *,
    expires_at: datetime,
    activated_at: datetime | None = None,
    token: str = "existing-token",
) -> SubscriptionToken:
    """Build a subscription token with sensible defaults for the given state."""
    return SubscriptionToken(
        id=1,
        token=token,
        created_at=datetime.now(UTC),
        activated_at=activated_at,
        expires_at=expires_at,
    )


def test_create_token_sets_expiry_and_unactivated_state() -> None:
    """create_token generates a non-empty token expiring after the given window."""
    repo = FakeSubscriptionTokenRepository()
    service = SubscriptionTokenService(repo)

    expires_in = 3600
    token = asyncio.run(service.create_token(expires_in_seconds=expires_in))

    assert token.token
    assert token.activated_at is None
    assert token.expires_at - token.created_at == timedelta(seconds=expires_in)
    assert repo.created_token is token


def test_validate_token_returns_token_when_valid() -> None:
    """A token that is unexpired and unactivated passes validation and is returned."""
    valid = _make_token(expires_at=datetime.now(UTC) + timedelta(hours=1))
    service = SubscriptionTokenService(FakeSubscriptionTokenRepository(valid))

    result = asyncio.run(service.validate_token("existing-token"))

    assert result is valid


def test_validate_token_raises_when_not_found() -> None:
    """A missing token raises ValueError('Invalid token')."""
    service = SubscriptionTokenService(FakeSubscriptionTokenRepository(None))

    with pytest.raises(ValueError, match="Invalid token"):
        asyncio.run(service.validate_token("missing"))


def test_validate_token_raises_when_expired() -> None:
    """An expired token raises ValueError('Token expired')."""
    expired = _make_token(expires_at=datetime.now(UTC) - timedelta(seconds=1))
    service = SubscriptionTokenService(FakeSubscriptionTokenRepository(expired))

    with pytest.raises(ValueError, match="Token expired"):
        asyncio.run(service.validate_token("existing-token"))


def test_validate_token_raises_when_already_activated() -> None:
    """An already-activated token raises ValueError('Token already activated')."""
    activated = _make_token(
        expires_at=datetime.now(UTC) + timedelta(hours=1),
        activated_at=datetime.now(UTC) - timedelta(minutes=5),
    )
    service = SubscriptionTokenService(FakeSubscriptionTokenRepository(activated))

    with pytest.raises(ValueError, match="Token already activated"):
        asyncio.run(service.validate_token("existing-token"))


def test_activate_token_sets_user_and_activation_and_persists() -> None:
    """activate_token links the user, stamps activated_at, and delegates to update_token."""
    valid = _make_token(expires_at=datetime.now(UTC) + timedelta(hours=1))
    repo = FakeSubscriptionTokenRepository(valid)
    service = SubscriptionTokenService(repo)
    user = User(
        id=42,
        first_name="Ada",
        last_name="Lovelace",
        username="ada",
        chat_id=99,
        is_subscribed=False,
    )

    result = asyncio.run(service.activate_token("existing-token", user))

    assert result.user_id == 42
    assert result.activated_at is not None
    assert repo.updated_token is result
