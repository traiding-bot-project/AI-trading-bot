"""PostgreSQL implementation of the UserRepository protocol."""

import logging

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.user import UserDB
from src.models.user import User, UserFilters

logger = logging.getLogger(__name__)


class PostgresUserRepository:
    """Implements the UserRepository protocol using PostgreSQL via SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the PostgresUserRepository with a persistent database session."""
        self._session = session
        logger.debug("PostgresUserRepository initialized")

    async def add_user(self, user: User) -> User:
        """Add a new user to the database."""
        logger.info(f"Adding new user to database: {user.username}")
        user_db = UserDB(**user.model_dump(exclude={"id"}))
        self._session.add(user_db)
        await self._session.commit()
        await self._session.refresh(user_db)
        logger.debug(f"User added with ID {user_db.id}")
        return User.model_validate(user_db)

    async def get_user_by_chat_id(self, chat_id: int) -> User | None:
        """Retrieve a user from the database by their Telegram chat ID."""
        logger.debug(f"Querying database for user with chat_id {chat_id}")
        stmt = select(UserDB).where(UserDB.chat_id == chat_id)
        result = await self._session.execute(stmt)
        user_db = result.scalar_one_or_none()
        if user_db:
            logger.debug(f"Found user: {user_db.username}")
        else:
            logger.debug(f"User not found with chat_id {chat_id}")
        return User.model_validate(user_db) if user_db else None

    async def get_all_users(self, filters: UserFilters) -> list[User]:
        """Retrieve all users from the database with optional filtering."""
        logger.debug(f"Querying all users with filters: {filters.model_dump(exclude_none=True)}")
        stmt = select(UserDB)

        if filters.is_subscribed is not None:
            logger.debug(f"Applying subscription filter: is_subscribed={filters.is_subscribed}")
            stmt = stmt.where(UserDB.is_subscribed == filters.is_subscribed)

        result = await self._session.execute(stmt)
        users = [User.model_validate(user) for user in result.scalars().all()]
        logger.debug(f"Retrieved {len(users)} users from database")
        return users

    async def update_user(self, user: User) -> User:
        """Update an existing user in the database."""
        logger.info(f"Updating user with chat_id {user.chat_id}")
        update_data = user.model_dump(exclude_unset=True, exclude={"id"})
        logger.debug(f"Update data: {update_data}")

        stmt = update(UserDB).where(UserDB.chat_id == user.chat_id).values(**update_data).returning(UserDB)

        result = await self._session.execute(stmt)
        updated_user_db = result.scalar_one_or_none()

        if not updated_user_db:
            logger.error(f"User not found for update: chat_id {user.chat_id}")
            raise ValueError(f"User with chat_id {user.chat_id} not found")

        await self._session.commit()
        logger.info(f"User updated successfully")
        return User.model_validate(updated_user_db)

    async def delete_user(self, user_id: int) -> bool:
        """Delete a user from the database by their ID."""
        logger.info(f"Deleting user with ID {user_id}")
        stmt = delete(UserDB).where(UserDB.id == user_id).returning(UserDB.id)
        result = await self._session.execute(stmt)
        deleted_id = result.scalar_one_or_none()

        await self._session.commit()
        
        if deleted_id:
            logger.info(f"User deleted successfully")
        else:
            logger.warning(f"User not found for deletion: ID {user_id}")
        
        return deleted_id is not None
