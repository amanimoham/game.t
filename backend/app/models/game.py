from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models._types import pg_enum
from app.models.enums import MonsterCode, SessionStatus
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.child import Child


class Level(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "levels"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    difficulty: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    required_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0, index=True)
    # Whether completing this level is required to unlock a reward.
    is_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    challenges: Mapped[list["Challenge"]] = relationship(
        back_populates="level",
        cascade="all, delete-orphan",
    )


class MonsterType(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Catalog of temptation ("monster") archetypes and their effects."""

    __tablename__ = "monster_types"

    code: Mapped[MonsterCode] = mapped_column(
        pg_enum(MonsterCode, "monster_code"),
        nullable=False,
        unique=True,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    effect: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    base_difficulty: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)

    challenges: Mapped[list["Challenge"]] = relationship(back_populates="monster_type")


class Challenge(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A single temptation-fighting scenario within a level."""

    __tablename__ = "challenges"

    level_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("levels.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    monster_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("monster_types.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    scenario: Mapped[str] = mapped_column(Text, nullable=False)
    # Array of choice objects: [{"key": "a", "label": "...", "kind": "wait"}, ...]
    choices: Mapped[list] = mapped_column(JSONB, nullable=False)
    correct_behavior: Mapped[str] = mapped_column(String(50), nullable=False)
    points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_final: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    level: Mapped["Level"] = relationship(back_populates="challenges")
    monster_type: Mapped["MonsterType"] = relationship(back_populates="challenges")


class GameSession(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """One play session; a child may leave and resume across sessions."""

    __tablename__ = "game_sessions"

    child_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("children.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    current_level_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("levels.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[SessionStatus] = mapped_column(
        pg_enum(SessionStatus, "session_status"),
        nullable=False,
        default=SessionStatus.ACTIVE,
        index=True,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    child: Mapped["Child"] = relationship()
