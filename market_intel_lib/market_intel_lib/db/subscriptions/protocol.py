"""Protocol definitions for subscription token repository interactions."""

from typing import Protocol

from market_intel_lib.models.subscription_token import SubscriptionToken


class SubscriptionTokenRepository(Protocol):
    """Protocol defining the interface for subscription token repository operations."""

    async def create_token(self, token: SubscriptionToken) -> SubscriptionToken:
        """Add a new subscription token to the repository."""
        ...

    async def list_tokens(self) -> list[SubscriptionToken]:
        """List all subscription tokens."""
        ...

    async def get_token_by_value(self, token_value: str) -> SubscriptionToken | None:
        """Retrieve a subscription token by its value."""
        ...

    async def list_tokens_by_username(self, username: str) -> list[SubscriptionToken]:
        """List all subscription tokens associated with a specific username."""
        ...

    async def update_token(self, token: SubscriptionToken) -> SubscriptionToken:
        """Update an existing subscription token's information."""
        ...
