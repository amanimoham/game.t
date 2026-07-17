from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import CreatedAtMixin

if TYPE_CHECKING:
    from app.models.child import Child


class ChildDecision(CreatedAtMixin, Base):
    """Append-only log of each choice a child makes in a challenge."""

    __tablename__ = "child_decisions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    child_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("children.id", ondelete="CASCADE"),
        nullable=False,
    )
    challenge_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("challenges.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("game_sessions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    selected_choice: Mapped[str] = mapped_column(String(50), nullable=False)
    response_time: Mapped[int | None] = mapped_column(Integer, nullable=True)  # ms
    score_change: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    __table_args__ = (
        Index("ix_child_decisions_child_created", "child_id", "created_at"),
    )


class ChildProfile(Base):
    """Rolling skill scores for a child (one row per child)."""

    __tablename__ = "child_profiles"

    child_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("children.id", ondelete="CASCADE"),
        primary_key=True,
    )
    patience_score: Mapped[Decimal] = mapped_column(
        Numeric(6, 2), nullable=False, default=0
    )
    saving_awareness_score: Mapped[Decimal] = mapped_column(
        Numeric(6, 2), nullable=False, default=0
    )
    impulse_control_score: Mapped[Decimal] = mapped_column(
        Numeric(6, 2), nullable=False, default=0
    )
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    child: Mapped["Child"] = relationship(back_populates="profile")


class BehaviorEvent(CreatedAtMixin, Base):
    """Append-only raw telemetry — fuel for future AI feature extraction.

    Modeled after open educational-game telemetry schemas (typed, timestamped,
    session-scoped events with a flexible JSONB payload).
    """

    __tablename__ = "behavior_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    child_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("children.id", ondelete="CASCADE"),
        nullable=False,
    )
    session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("game_sessions.id", ondelete="SET NULL"),
        nullable=True,
    )
    event_name: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    sequence_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    elapsed_ms: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    level_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("levels.id", ondelete="SET NULL"),
        nullable=True,
    )
    monster_type_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("monster_types.id", ondelete="SET NULL"),
        nullable=True,
    )
    event_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    __table_args__ = (
        Index("ix_behavior_events_child_created", "child_id", "created_at"),
    )
