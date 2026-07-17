from __future__ import annotations

import uuid

from sqlalchemy import BigInteger, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.models._types import pg_enum
from app.models.enums import ActorType
from app.models.mixins import CreatedAtMixin


class AuditLog(CreatedAtMixin, Base):
    """Append-only record of important, security-relevant actions."""

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    actor_type: Mapped[ActorType] = mapped_column(
        pg_enum(ActorType, "actor_type"),
        nullable=False,
    )
    actor_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_type: Mapped[str | None] = mapped_column(String(60), nullable=True)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    # Column is named "metadata" per the ERD; attribute renamed to avoid the
    # reserved Declarative ``metadata`` name.
    event_metadata: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    ip_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
