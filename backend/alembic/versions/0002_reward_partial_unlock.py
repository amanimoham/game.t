"""reward partial unlock

Revision ID: 0002_reward_partial_unlock
Revises: 0001_initial_schema
Create Date: 2026-07-17

Adds gradual-unlock support: unlocked_amount/progress_pct on reward_orders and
an append-only reward_unlock_events audit table.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0002_reward_partial_unlock"
down_revision: Union[str, None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_NOW = sa.text("now()")


def upgrade() -> None:
    op.add_column(
        "reward_orders",
        sa.Column(
            "unlocked_amount",
            sa.Numeric(precision=12, scale=2),
            server_default=sa.text("0"),
            nullable=False,
        ),
    )
    op.add_column(
        "reward_orders",
        sa.Column(
            "progress_pct",
            sa.SmallInteger(),
            server_default=sa.text("0"),
            nullable=False,
        ),
    )

    op.create_table(
        "reward_unlock_events",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("reward_order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("reason", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.ForeignKeyConstraint(
            ["reward_order_id"], ["reward_orders.id"],
            name="fk_reward_unlock_events_reward_order_id_reward_orders",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_reward_unlock_events"),
    )
    op.create_index(
        "ix_reward_unlock_events_reward_order_id",
        "reward_unlock_events",
        ["reward_order_id"],
    )


def downgrade() -> None:
    op.drop_table("reward_unlock_events")
    op.drop_column("reward_orders", "progress_pct")
    op.drop_column("reward_orders", "unlocked_amount")
