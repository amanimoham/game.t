"""Redis-backed refresh-token store: enables rotation and revocation.

Each valid refresh token's jti maps to its subject. Refreshing revokes the old
jti and issues a new one (rotation); logout deletes the jti.
"""
from __future__ import annotations

from app.security.redis_client import get_redis

_PREFIX = "refresh:"


async def store(jti: str, subject: str, ttl_seconds: int) -> None:
    await get_redis().set(_PREFIX + jti, subject, ex=ttl_seconds)


async def is_valid(jti: str, subject: str) -> bool:
    value = await get_redis().get(_PREFIX + jti)
    return value == subject


async def revoke(jti: str) -> None:
    await get_redis().delete(_PREFIX + jti)
