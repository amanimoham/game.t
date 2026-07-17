from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.models._types import pg_enum
from app.models.enums import ConsentType
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class ParentalConsent(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """COPPA/GDPR-K record: a parent's documented consent for a child."""

    __tablename__ = "parental_consents"

    parent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    child_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("children.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    consent_type: Mapped[ConsentType] = mapped_column(
        pg_enum(ConsentType, "consent_type"),
        nullable=False,
    )
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    # Hashed, never the raw IP.
    ip_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    policy_version: Mapped[str] = mapped_column(String(32), nullable=False)
