"""Database models and services for managing subscription tokens in the Telegram user app service."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.declarative_base import Base

if TYPE_CHECKING:
    from src.db.users.user import UserDB


class SubscriptionTokenDB(Base):
    """Database model representing a subscription token."""

    __tablename__ = "subscription_tokens"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    token: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user: Mapped[UserDB | None] = relationship(back_populates="tokens")

    def __repr__(self) -> str:
        """Returns a string representation of the SubscriptionTokenDB instance."""
        return f"<SubscriptionTokenDB(token={self.token}, user_id={self.user_id}, expires_at={self.expires_at})>"
