"""open banking (simulated): bank connections + saving goals

Revision ID: 0003_open_banking
Revises: 0002_reward_partial_unlock
Create Date: 2026-07-17
"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0003_open_banking"
down_revision: Union[str, None] = "0002_reward_partial_unlock"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_NOW = sa.text("now()")

connection_status = postgresql.ENUM("connected", "disconnected", name="connection_status", create_type=False)
goal_status = postgresql.ENUM("active", "achieved", "cancelled", name="goal_status", create_type=False)


def upgrade() -> None:
    bind = op.get_bind()
    connection_status.create(bind, checkfirst=True)
    goal_status.create(bind, checkfirst=True)

    op.create_table(
        "bank_connections",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("bank_name", sa.String(length=120), nullable=False),
        sa.Column("status", connection_status, nullable=False),
        sa.Column("consent_granted", sa.Boolean(), nullable=False),
        sa.Column("connected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.ForeignKeyConstraint(["parent_id"], ["users.id"], name="fk_bank_connections_parent_id_users", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_bank_connections"),
        sa.UniqueConstraint("parent_id", name="uq_bank_connections_parent_id"),
    )
    op.create_index("ix_bank_connections_parent_id", "bank_connections", ["parent_id"])

    op.create_table(
        "saving_goals",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("child_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("target_amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("current_amount", sa.Numeric(precision=12, scale=2), server_default=sa.text("0"), nullable=False),
        sa.Column("currency", sa.String(length=16), server_default=sa.text("'robux'"), nullable=False),
        sa.Column("target_date", sa.Date(), nullable=True),
        sa.Column("status", goal_status, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.ForeignKeyConstraint(["parent_id"], ["users.id"], name="fk_saving_goals_parent_id_users", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"], name="fk_saving_goals_child_id_children", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_saving_goals"),
    )
    op.create_index("ix_saving_goals_parent_id", "saving_goals", ["parent_id"])


def downgrade() -> None:
    op.drop_table("saving_goals")
    op.drop_table("bank_connections")
    bind = op.get_bind()
    goal_status.drop(bind, checkfirst=True)
    connection_status.drop(bind, checkfirst=True)
