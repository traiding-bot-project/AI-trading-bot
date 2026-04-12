"""Implements the PostgresUserRepository for managing user data in a PostgreSQL database using SQLAlchemy."""

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.user import UserDB
from src.models.user import User, UserFilters


class PostgresUserRepository:
    """Implements the UserRepository protocol for managing user data in a PostgreSQL database using SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        """Initializes the PostgresUserRepository with a given SQLAlchemy session."""
        self._session = session

    async def add_user(self, user: User) -> User:
        """Adds a new user to the repository and returns the created User object."""
        user_db = UserDB(**user.model_dump(exclude={"id"}))
        self._session.add(user_db)
        await self._session.commit()
        await self._session.refresh(user_db)
        return User.model_validate(user_db)

    async def get_user_by_chat_id(self, chat_id: int) -> User | None:
        """Retrieves a user by their Telegram chat ID. Returns None if the user is not found."""
        stmt = select(UserDB).where(UserDB.chat_id == chat_id)
        result = await self._session.execute(stmt)
        user_db = result.scalar_one_or_none()
        return User.model_validate(user_db) if user_db else None

    async def get_all_users(self, filters: UserFilters) -> list[User]:
        """Returns a list of users in the repository."""
        stmt = select(UserDB)

        if filters.is_subscribed is not None:
            stmt = stmt.where(UserDB.is_subscribed == filters.is_subscribed)

        result = await self._session.execute(stmt)
        return [User.model_validate(user) for user in result.scalars().all()]

    async def update_user(self, user: User) -> User:
        """Updates an existing user in the repository and returns the updated User object."""
        update_data = user.model_dump(exclude_unset=True, exclude={"id"})

        stmt = update(UserDB).where(UserDB.chat_id == user.chat_id).values(**update_data).returning(UserDB)

        result = await self._session.execute(stmt)
        updated_user_db = result.scalar_one_or_none()

        if not updated_user_db:
            raise ValueError(f"User with chat_id {user.chat_id} not found")

        await self._session.commit()
        return User.model_validate(updated_user_db)

    async def delete_user(self, user_id: int) -> bool:
        """Deletes a user by their ID. Returns True if deletion was successful, False otherwise."""
        stmt = delete(UserDB).where(UserDB.id == user_id).returning(UserDB.id)
        result = await self._session.execute(stmt)
        deleted_id = result.scalar_one_or_none()

        await self._session.commit()
        return deleted_id is not None
