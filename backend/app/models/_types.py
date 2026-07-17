"""Shared helpers for mapping Python enums to native Postgres ENUM types."""
from __future__ import annotations

import enum
from typing import TypeVar

from sqlalchemy import Enum as SAEnum

_E = TypeVar("_E", bound=enum.Enum)


def pg_enum(python_enum: type[_E], name: str) -> SAEnum:
    """Native Postgres ENUM that stores the member *value* (clean lowercase)."""
    return SAEnum(
        python_enum,
        name=name,
        native_enum=True,
        values_callable=lambda e: [member.value for member in e],
        validate_strings=True,
    )
