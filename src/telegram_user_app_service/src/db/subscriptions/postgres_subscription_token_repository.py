"""PostgreSQL implementation of the SubscriptionTokenRepository for the Telegram user app service."""

import logging

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.subscriptions.subscription_token import SubscriptionTokenDB
from src.db.users.user import UserDB
from src.models.subscription_token import SubscriptionToken

logger = logging.getLogger(__name__)


class PostgresSubscriptionTokenRepository:
    """Implements subscription token persistence using PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with a given SQLAlchemy AsyncSession."""
        self._session = session
        logger.debug("PostgresSubscriptionTokenRepository initialized")

    async def create_token(self, token: SubscriptionToken) -> SubscriptionToken:
        """Create and persist a new subscription token in the database."""
        logger.info("Creating new subscription token in the database")
        token_db = SubscriptionTokenDB(**token.model_dump(exclude={"id"}))
        self._session.add(token_db)
        await self._session.commit()
        await self._session.refresh(token_db)
        logger.debug("Subscription token created")
        return SubscriptionToken.model_validate(token_db)

    async def list_tokens(self) -> list[SubscriptionToken]:
        """List all subscription tokens."""
        logger.debug("Listing all subscription tokens from the database")
        stmt = select(SubscriptionTokenDB)
        result = await self._session.execute(stmt)
        return [SubscriptionToken.model_validate(token_db) for token_db in result.scalars().all()]

    async def get_token_by_value(self, token_value: str) -> SubscriptionToken | None:
        """Retrieve a subscription token by its exact token value."""
        logger.debug("Querying subscription token by value")
        stmt = select(SubscriptionTokenDB).where(SubscriptionTokenDB.token == token_value)
        result = await self._session.execute(stmt)
        token_db = result.scalar_one_or_none()
        return SubscriptionToken.model_validate(token_db) if token_db else None

    async def list_tokens_by_user_id(self, user_id: int) -> list[SubscriptionToken]:
        """List all subscription tokens associated with a given user ID."""
        logger.debug(f"Listing subscription tokens for user_id {user_id}")
        stmt = select(SubscriptionTokenDB).where(SubscriptionTokenDB.user_id == user_id)
        result = await self._session.execute(stmt)
        return [SubscriptionToken.model_validate(token_db) for token_db in result.scalars().all()]

    async def list_tokens_by_chat_id(self, chat_id: int) -> list[SubscriptionToken]:
        """List all subscription tokens associated with a given Telegram chat ID."""
        logger.debug(f"Listing subscription tokens for chat_id {chat_id}")
        stmt = (
            select(SubscriptionTokenDB)
            .join(UserDB, SubscriptionTokenDB.user_id == UserDB.id)
            .where(UserDB.chat_id == chat_id)
        )
        result = await self._session.execute(stmt)
        return [SubscriptionToken.model_validate(token_db) for token_db in result.scalars().all()]

    async def list_tokens_by_username(self, username: str) -> list[SubscriptionToken]:
        """List all subscription tokens associated with a given username."""
        logger.debug(f"Listing subscription tokens for username {username}")
        stmt = (
            select(SubscriptionTokenDB)
            .join(UserDB, SubscriptionTokenDB.user_id == UserDB.id)
            .where(UserDB.username == username)
        )
        result = await self._session.execute(stmt)
        return [SubscriptionToken.model_validate(token_db) for token_db in result.scalars().all()]

    async def update_token(self, token: SubscriptionToken) -> SubscriptionToken:
        """Update an existing subscription token in the database."""
        logger.debug(f"Updating subscription token with id {token.id}")
        stmt = (
            update(SubscriptionTokenDB)
            .where(SubscriptionTokenDB.id == token.id)
            .values(**token.model_dump(exclude={"id"}))
            .returning(SubscriptionTokenDB)
        )
        result = await self._session.execute(stmt)
        await self._session.commit()
        updated_token_db = result.scalar_one()
        logger.debug("Subscription token updated")
        return SubscriptionToken.model_validate(updated_token_db)
