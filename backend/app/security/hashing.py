"""Password / PIN hashing (argon2)."""
from __future__ import annotations

from passlib.context import CryptContext

_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_secret(secret: str) -> str:
    return _context.hash(secret)


def verify_secret(secret: str, hashed: str | None) -> bool:
    if not hashed:
        return False
    return _context.verify(secret, hashed)
