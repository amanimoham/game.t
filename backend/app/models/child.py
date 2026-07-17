from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models._types import pg_enum
from app.models.enums import AgeGroup
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.analytics import ChildProfile
    from app.models.user import User


class Child(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A child profile managed by a parent. No sensitive PII is stored.

    Authentication is a parent-managed PIN (hashed); there is no email/password
    for the child (COPPA-minimal footprint).
    """

    __tablename__ = "children"

    parent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    nickname: Mapped[str] = mapped_column(String(50), nullable=False)
    age_group: Mapped[AgeGroup] = mapped_column(
        pg_enum(AgeGroup, "age_group"),
        nullable=False,
    )
    # Nullable: parent may create the profile before setting the child's PIN.
    pin_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    parent: Mapped["User"] = relationship(back_populates="children")
    profile: Mapped["ChildProfile | None"] = relationship(
        back_populates="child",
        uselist=False,
        cascade="all, delete-orphan",
    )
