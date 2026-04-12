"""Defines the UserDB model for the Telegram User App Service."""

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models in the Telegram User App Service."""

    pass


class UserDB(Base):
    """Represents a user in the database for the Telegram User App Service."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(64), nullable=False)
    last_name: Mapped[str] = mapped_column(String(64), nullable=False)
    username: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    is_subscribed: Mapped[bool] = mapped_column(default=False, nullable=False)

    def __repr__(self) -> str:
        """Returns a string representation of the UserDB instance."""
        return f"<UserDB(username={self.username}, chat_id={self.chat_id}, is_subscribed={self.is_subscribed})>"
