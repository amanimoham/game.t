from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.models._types import pg_enum
from app.models.enums import ConnectionStatus, GoalStatus
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class BankConnection(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A parent's (simulated) Open Banking connection.

    MVP stores NO sensitive banking data — only the chosen institution name,
    consent flag, and sync timestamps. Architecture is ready to swap the
    simulated provider for a real Saudi Open Banking aggregator.
    """

    __tablename__ = "bank_connections"

    parent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # one active connection record per parent
        index=True,
    )
    bank_name: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[ConnectionStatus] = mapped_column(
        pg_enum(ConnectionStatus, "connection_status"),
        nullable=False,
        default=ConnectionStatus.DISCONNECTED,
    )
    consent_granted: Mapped[bool] = mapped_column(nullable=False, default=False)
    connected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class SavingGoal(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A saving goal a parent sets (optionally tied to a child's reward journey)."""

    __tablename__ = "saving_goals"

    parent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    child_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("children.id", ondelete="SET NULL"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    target_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    current_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=0, server_default=text("0")
    )
    currency: Mapped[str] = mapped_column(String(16), nullable=False, default="robux", server_default=text("'robux'"))
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[GoalStatus] = mapped_column(
        pg_enum(GoalStatus, "goal_status"),
        nullable=False,
        default=GoalStatus.ACTIVE,
    )
