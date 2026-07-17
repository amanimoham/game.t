from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models._types import pg_enum
from app.models.enums import UserRole
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.child import Child


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Parent (paying account owner) or admin. Children are NOT users."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        pg_enum(UserRole, "user_role"),
        nullable=False,
        default=UserRole.PARENT,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    children: Mapped[list["Child"]] = relationship(
        back_populates="parent",
        cascade="all, delete-orphan",
    )
