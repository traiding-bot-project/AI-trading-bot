"""subscriptions token table created.

Revision ID: 9b90143ae775
Revises: 2d14726b9fbe
Create Date: 2026-05-14 20:57:03.066037

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9b90143ae775"
down_revision: str | Sequence[str] | None = "2d14726b9fbe"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # This revision was originally produced by `--autogenerate` against a database
    # where `subscription_tokens` already existed (created out-of-band), so it only
    # captured the diff -- ALTERs against a table nothing ever created. That made
    # `alembic upgrade head` impossible on an empty database. Replaced with the
    # create_table it should always have been; mirrors SubscriptionTokenDB in
    # market_intel_lib/db/subscriptions/subscription_token.py.
    op.create_table(
        "subscription_tokens",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("token", sa.String(length=128), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token"),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("subscription_tokens_user_id_fkey"),
            ondelete="SET NULL",
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("subscription_tokens")
