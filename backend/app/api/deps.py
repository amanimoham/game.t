"""Auth dependencies: extract the bearer token and resolve the current actor."""
from __future__ import annotations

import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.child import Child
from app.models.user import User
from app.security.tokens import TokenError, decode_token

__all__ = ["get_db", "get_current_parent", "get_current_child"]

_bearer = HTTPBearer(auto_error=False)


def _unauthorized(detail: str = "Not authenticated") -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


async def _payload(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict:
    if creds is None:
        raise _unauthorized()
    try:
        return decode_token(creds.credentials, expected_type="access")
    except TokenError as exc:
        raise _unauthorized(str(exc)) from exc


async def get_current_parent(
    payload: dict = Depends(_payload),
    db: AsyncSession = Depends(get_db),
) -> User:
    if payload.get("role") not in ("parent", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Parent role required")
    try:
        user_id = uuid.UUID(payload["sub"])
    except (KeyError, ValueError) as exc:
        raise _unauthorized("Invalid subject") from exc
    user = await db.get(User, user_id)
    if user is None or not user.is_active:
        raise _unauthorized("User not found or inactive")
    return user


async def get_current_child(
    payload: dict = Depends(_payload),
    db: AsyncSession = Depends(get_db),
) -> Child:
    if payload.get("role") != "child":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Child session required")
    try:
        child_id = uuid.UUID(payload["sub"])
    except (KeyError, ValueError) as exc:
        raise _unauthorized("Invalid subject") from exc
    child = await db.get(Child, child_id)
    if child is None or not child.is_active:
        raise _unauthorized("Child not found or inactive")
    return child
