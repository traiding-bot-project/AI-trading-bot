"""Initializes the database connection and provides factory functions for creating repository and service instances."""

import threading
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.db.postgres_user_repository import PostgresUserRepository
from src.db.user_service import UserService
from src.models.infisical import InfisicalSecretsKeys
from src.secrets import secrets_manager
from src.settings import settings
from src.utils.get_resource_url import get_resource_url

db_password = secrets_manager.get_secret(InfisicalSecretsKeys.DB_PASSWORD)
db_params = settings.database.model_dump()
api_path = db_params.pop("database", None)


_db_url = get_resource_url(password=db_password, api=api_path, **db_params)

_thread_local = threading.local()


def _get_session_factory() -> Any:
    """Return a session factory scoped to the current thread (and its event loop)."""
    if not hasattr(_thread_local, "session_factory"):
        engine = create_async_engine(_db_url)
        _thread_local.session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    return _thread_local.session_factory


@asynccontextmanager
async def user_service_context() -> AsyncGenerator[UserService]:
    """Async context manager for providing a UserService instance."""
    session_factory = _get_session_factory()
    async with session_factory() as session:
        yield UserService(PostgresUserRepository(session))


async def get_user_service() -> AsyncGenerator[UserService]:
    """Factory function to create a UserService instance."""
    async with user_service_context() as user_service:
        yield user_service
