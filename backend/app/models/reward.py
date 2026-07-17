from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, Numeric, SmallInteger, String, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models._types import pg_enum
from app.models.enums import RewardStatus, RewardType
from app.models.mixins import CreatedAtMixin, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    pass


class RewardOrder(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A funded, locked reward that unlocks *gradually* as the child progresses.

    ``unlocked_amount`` / ``progress_pct`` track partial release; the immutable
    ``reward_unlock_events`` rows are the authoritative audit of every release.
    ``unlock_criteria`` is a snapshot captured at creation so later content
    changes never alter an in-flight order's requirements.
    """

    __tablename__ = "reward_orders"

    parent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    child_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("children.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    reward_type: Mapped[RewardType] = mapped_column(
        pg_enum(RewardType, "reward_type"),
        nullable=False,
        default=RewardType.ROBUX,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[RewardStatus] = mapped_column(
        pg_enum(RewardStatus, "reward_status"),
        nullable=False,
        default=RewardStatus.LOCKED,
        index=True,
    )
    unlocked_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=0, server_default=text("0")
    )
    progress_pct: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, server_default=text("0")
    )
    unlock_criteria: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    delivered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    unlock_events: Mapped[list["RewardUnlockEvent"]] = relationship(
        back_populates="reward_order",
        cascade="all, delete-orphan",
        order_by="RewardUnlockEvent.id",
    )


class RewardUnlockEvent(CreatedAtMixin, Base):
    """Append-only record of each partial (or final) release of a reward."""

    __tablename__ = "reward_unlock_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    reward_order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reward_orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    reason: Mapped[str] = mapped_column(String(50), nullable=False)

    reward_order: Mapped["RewardOrder"] = relationship(back_populates="unlock_events")
