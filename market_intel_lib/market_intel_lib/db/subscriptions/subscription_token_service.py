"""High-level service for managing subscription tokens in the Telegram user app service."""

import logging
import secrets
from datetime import UTC, datetime, timedelta

from market_intel_lib.constants import SUBSCRIPTION_TOKEN_EXPIRATION_SECONDS
from market_intel_lib.db.subscriptions.protocol import SubscriptionTokenRepository
from market_intel_lib.models.subscription_token import SubscriptionToken
from market_intel_lib.models.user import User

logger = logging.getLogger(__name__)


class SubscriptionTokenService:
    """High-level service for managing subscription tokens."""

    def __init__(
        self,
        repository: SubscriptionTokenRepository,
    ) -> None:
        """Initialize the SubscriptionTokenService with the given repository."""
        self._repo = repository
        logger.debug("SubscriptionTokenService initialized")

    async def create_token(
        self, expires_in_seconds: int = SUBSCRIPTION_TOKEN_EXPIRATION_SECONDS
    ) -> SubscriptionToken:
        """Create and persist a new subscription token."""
        now = datetime.now(UTC)
        expires_at = now + timedelta(seconds=expires_in_seconds)

        token = SubscriptionToken(
            token=secrets.token_urlsafe(48),
            created_at=now,
            activated_at=None,
            expires_at=expires_at,
        )

        logger.info(
            f"Generating new subscription token that expires at {expires_at.isoformat()}"
        )
        return await self._repo.create_token(token)

    async def list_tokens(self) -> list[SubscriptionToken]:
        """List all subscription tokens."""
        return await self._repo.list_tokens()

    async def get_token_by_value(self, token_value: str) -> SubscriptionToken | None:
        """Retrieve a subscription token by its exact token value."""
        return await self._repo.get_token_by_value(token_value)

    async def list_tokens_for_username(self, username: str) -> list[SubscriptionToken]:
        """List all subscription tokens for a given username."""
        return await self._repo.list_tokens_by_username(username)

    async def validate_token(self, token_value: str) -> SubscriptionToken:
        """Ensure the token is valid, not expired, and not already activated."""
        token = await self.get_token_by_value(token_value)
        if not token:
            logger.warning("Token validation failed: token not found")
            raise ValueError("Invalid token")

        now = datetime.now(UTC)
        if token.expires_at <= now:
            logger.warning("Token validation failed: token expired")
            raise ValueError("Token expired")

        if token.activated_at is not None:
            logger.warning("Token validation failed: token already activated")
            raise ValueError("Token already activated")

        return token

    async def activate_token(self, token_value: str, user: User) -> SubscriptionToken:
        """Activate the token and associate it with a user."""
        token = await self.validate_token(token_value)

        now = datetime.now(UTC)
        token.user_id = user.id
        token.activated_at = now

        return await self._repo.update_token(token)
