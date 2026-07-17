"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-07-17

Creates the full baseline schema: users, children, parental consents, reward
orders, game content (levels/monster types/challenges), sessions, analytics
(decisions/profiles/behavior events) and audit logs.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ---- Native ENUM types (created explicitly, referenced with create_type=False) ----
user_role = postgresql.ENUM("parent", "admin", name="user_role", create_type=False)
age_group = postgresql.ENUM("5-7", "8-10", "11-13", name="age_group", create_type=False)
consent_type = postgresql.ENUM(
    "data_collection", "gameplay", name="consent_type", create_type=False
)
reward_type = postgresql.ENUM("robux", name="reward_type", create_type=False)
reward_status = postgresql.ENUM(
    "locked", "in_progress", "completed", "delivered", "cancelled",
    name="reward_status", create_type=False,
)
session_status = postgresql.ENUM(
    "active", "completed", "abandoned", name="session_status", create_type=False
)
monster_code = postgresql.ENUM(
    "instant_reward", "social_pressure", "spending", "limited_offer",
    name="monster_code", create_type=False,
)
actor_type = postgresql.ENUM(
    "parent", "child", "admin", "system", name="actor_type", create_type=False
)

_ALL_ENUMS = [
    user_role, age_group, consent_type, reward_type,
    reward_status, session_status, monster_code, actor_type,
]

_NOW = sa.text("now()")


def upgrade() -> None:
    bind = op.get_bind()
    for enum_type in _ALL_ENUMS:
        enum_type.create(bind, checkfirst=True)

    # ---- users ----
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", user_role, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # ---- levels ----
    op.create_table(
        "levels",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("difficulty", sa.SmallInteger(), nullable=False),
        sa.Column("required_score", sa.Integer(), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("is_required", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_levels"),
    )
    op.create_index("ix_levels_order_index", "levels", ["order_index"])

    # ---- monster_types ----
    op.create_table(
        "monster_types",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", monster_code, nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("effect", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("base_difficulty", sa.SmallInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_monster_types"),
        sa.UniqueConstraint("code", name="uq_monster_types_code"),
    )

    # ---- children ----
    op.create_table(
        "children",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("nickname", sa.String(length=50), nullable=False),
        sa.Column("age_group", age_group, nullable=False),
        sa.Column("pin_hash", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.ForeignKeyConstraint(
            ["parent_id"], ["users.id"],
            name="fk_children_parent_id_users", ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_children"),
    )
    op.create_index("ix_children_parent_id", "children", ["parent_id"])

    # ---- parental_consents ----
    op.create_table(
        "parental_consents",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("child_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("consent_type", consent_type, nullable=False),
        sa.Column("granted_at", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.Column("ip_hash", sa.String(length=128), nullable=True),
        sa.Column("policy_version", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.ForeignKeyConstraint(
            ["parent_id"], ["users.id"],
            name="fk_parental_consents_parent_id_users", ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["child_id"], ["children.id"],
            name="fk_parental_consents_child_id_children", ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_parental_consents"),
    )
    op.create_index("ix_parental_consents_parent_id", "parental_consents", ["parent_id"])
    op.create_index("ix_parental_consents_child_id", "parental_consents", ["child_id"])

    # ---- reward_orders ----
    op.create_table(
        "reward_orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("child_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reward_type", reward_type, nullable=False),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("status", reward_status, nullable=False),
        sa.Column("unlock_criteria", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.ForeignKeyConstraint(
            ["parent_id"], ["users.id"],
            name="fk_reward_orders_parent_id_users", ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["child_id"], ["children.id"],
            name="fk_reward_orders_child_id_children", ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_reward_orders"),
    )
    op.create_index("ix_reward_orders_parent_id", "reward_orders", ["parent_id"])
    op.create_index("ix_reward_orders_child_id", "reward_orders", ["child_id"])
    op.create_index("ix_reward_orders_status", "reward_orders", ["status"])

    # ---- challenges ----
    op.create_table(
        "challenges",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("level_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("monster_type_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("scenario", sa.Text(), nullable=False),
        sa.Column("choices", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("correct_behavior", sa.String(length=50), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("is_final", sa.Boolean(), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.ForeignKeyConstraint(
            ["level_id"], ["levels.id"],
            name="fk_challenges_level_id_levels", ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["monster_type_id"], ["monster_types.id"],
            name="fk_challenges_monster_type_id_monster_types", ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_challenges"),
    )
    op.create_index("ix_challenges_level_id", "challenges", ["level_id"])
    op.create_index("ix_challenges_monster_type_id", "challenges", ["monster_type_id"])

    # ---- game_sessions ----
    op.create_table(
        "game_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("child_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("current_level_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", session_status, nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.ForeignKeyConstraint(
            ["child_id"], ["children.id"],
            name="fk_game_sessions_child_id_children", ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["current_level_id"], ["levels.id"],
            name="fk_game_sessions_current_level_id_levels", ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_game_sessions"),
    )
    op.create_index("ix_game_sessions_child_id", "game_sessions", ["child_id"])
    op.create_index("ix_game_sessions_status", "game_sessions", ["status"])

    # ---- child_decisions (append-only) ----
    op.create_table(
        "child_decisions",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("child_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("challenge_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("selected_choice", sa.String(length=50), nullable=False),
        sa.Column("response_time", sa.Integer(), nullable=True),
        sa.Column("score_change", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.ForeignKeyConstraint(
            ["child_id"], ["children.id"],
            name="fk_child_decisions_child_id_children", ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["challenge_id"], ["challenges.id"],
            name="fk_child_decisions_challenge_id_challenges", ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["session_id"], ["game_sessions.id"],
            name="fk_child_decisions_session_id_game_sessions", ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_child_decisions"),
    )
    op.create_index("ix_child_decisions_challenge_id", "child_decisions", ["challenge_id"])
    op.create_index("ix_child_decisions_session_id", "child_decisions", ["session_id"])
    op.create_index(
        "ix_child_decisions_child_created", "child_decisions", ["child_id", "created_at"]
    )

    # ---- child_profiles ----
    op.create_table(
        "child_profiles",
        sa.Column("child_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("patience_score", sa.Numeric(precision=6, scale=2), nullable=False),
        sa.Column("saving_awareness_score", sa.Numeric(precision=6, scale=2), nullable=False),
        sa.Column("impulse_control_score", sa.Numeric(precision=6, scale=2), nullable=False),
        sa.Column("last_updated", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.ForeignKeyConstraint(
            ["child_id"], ["children.id"],
            name="fk_child_profiles_child_id_children", ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("child_id", name="pk_child_profiles"),
    )

    # ---- behavior_events (append-only) ----
    op.create_table(
        "behavior_events",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("child_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("event_name", sa.String(length=80), nullable=False),
        sa.Column("sequence_index", sa.Integer(), nullable=True),
        sa.Column("elapsed_ms", sa.BigInteger(), nullable=True),
        sa.Column("level_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("monster_type_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("event_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.ForeignKeyConstraint(
            ["child_id"], ["children.id"],
            name="fk_behavior_events_child_id_children", ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["session_id"], ["game_sessions.id"],
            name="fk_behavior_events_session_id_game_sessions", ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["level_id"], ["levels.id"],
            name="fk_behavior_events_level_id_levels", ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["monster_type_id"], ["monster_types.id"],
            name="fk_behavior_events_monster_type_id_monster_types", ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_behavior_events"),
    )
    op.create_index("ix_behavior_events_event_name", "behavior_events", ["event_name"])
    op.create_index(
        "ix_behavior_events_child_created", "behavior_events", ["child_id", "created_at"]
    )

    # ---- audit_logs (append-only) ----
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("actor_type", actor_type, nullable=False),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("entity_type", sa.String(length=60), nullable=True),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("ip_hash", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=_NOW, nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_audit_logs"),
    )
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("behavior_events")
    op.drop_table("child_profiles")
    op.drop_table("child_decisions")
    op.drop_table("game_sessions")
    op.drop_table("challenges")
    op.drop_table("reward_orders")
    op.drop_table("parental_consents")
    op.drop_table("children")
    op.drop_table("monster_types")
    op.drop_table("levels")
    op.drop_table("users")

    bind = op.get_bind()
    for enum_type in reversed(_ALL_ENUMS):
        enum_type.drop(bind, checkfirst=True)
