"""JWT creation/verification for access & refresh tokens."""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from app.core.config import settings


class TokenError(Exception):
    """Raised when a token is invalid, expired, or of the wrong type."""


def _now() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(sub: str, role: str, extra: dict[str, Any] | None = None) -> str:
    payload: dict[str, Any] = {
        "sub": str(sub),
        "role": role,
        "type": "access",
        "iat": _now(),
        "exp": _now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        **(extra or {}),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(sub: str, role: str) -> tuple[str, str, int]:
    """Return (token, jti, ttl_seconds)."""
    jti = str(uuid.uuid4())
    ttl_seconds = settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400
    payload: dict[str, Any] = {
        "sub": str(sub),
        "role": role,
        "type": "refresh",
        "jti": jti,
        "iat": _now(),
        "exp": _now() + timedelta(seconds=ttl_seconds),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, jti, ttl_seconds


def decode_token(token: str, expected_type: str | None = None) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except jwt.PyJWTError as exc:  # expired, bad signature, malformed
        raise TokenError(str(exc)) from exc
    if expected_type and payload.get("type") != expected_type:
        raise TokenError(f"expected {expected_type} token")
    return payload
