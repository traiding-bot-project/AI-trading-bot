"""SQLAlchemy ORM models for Telegram user database persistence."""

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from market_intel_lib.db.declarative_base import Base

if TYPE_CHECKING:
    from market_intel_lib.db.subscriptions.subscription_token import SubscriptionTokenDB


class UserDB(Base):
    """Database model representing a user in PostgreSQL."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(64), nullable=False)
    last_name: Mapped[str] = mapped_column(String(64), nullable=False)
    username: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    is_subscribed: Mapped[bool] = mapped_column(default=False, nullable=False)

    tokens: Mapped[list[SubscriptionTokenDB]] = relationship(
        back_populates="user", lazy="select"
    )

    def __repr__(self) -> str:
        """Returns a string representation of the UserDB instance."""
        return f"<UserDB(username={self.username}, chat_id={self.chat_id}, is_subscribed={self.is_subscribed})>"
