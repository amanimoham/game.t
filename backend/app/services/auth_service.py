"""Parent authentication + token lifecycle (issue / rotate / revoke)."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.models.enums import ActorType, UserRole
from app.models.user import User
from app.schemas.common import TokenPair
from app.security import refresh_store
from app.security.hashing import hash_secret, verify_secret
from app.security.tokens import (
    TokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
)


class AuthError(Exception):
    """Raised for invalid credentials / tokens (mapped to 401 by the API)."""


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def register_parent(self, email: str, password: str) -> User:
        email = email.strip().lower()
        existing = await self.db.execute(select(User).where(User.email == email))
        if existing.scalar_one_or_none() is not None:
            raise AuthError("Email already registered")
        user = User(
            email=email,
            password_hash=hash_secret(password),
            role=UserRole.PARENT,
            is_active=True,
        )
        self.db.add(user)
        await self.db.flush()
        self.db.add(
            AuditLog(
                actor_type=ActorType.PARENT,
                actor_id=user.id,
                action="auth.parent_registered",
                entity_type="user",
                entity_id=user.id,
            )
        )
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def authenticate_parent(self, email: str, password: str) -> User:
        email = email.strip().lower()
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user is None or not user.is_active or not verify_secret(password, user.password_hash):
            raise AuthError("Invalid email or password")
        return user

    async def issue_tokens(self, subject: str, role: str) -> TokenPair:
        access = create_access_token(subject, role)
        refresh, jti, ttl = create_refresh_token(subject, role)
        await refresh_store.store(jti, subject, ttl)
        return TokenPair(access_token=access, refresh_token=refresh)

    async def rotate(self, refresh_token: str) -> TokenPair:
        try:
            payload = decode_token(refresh_token, expected_type="refresh")
        except TokenError as exc:
            raise AuthError(str(exc)) from exc
        jti, subject, role = payload.get("jti"), payload.get("sub"), payload.get("role")
        if not jti or not subject or not await refresh_store.is_valid(jti, subject):
            raise AuthError("Refresh token is invalid or revoked")
        await refresh_store.revoke(jti)  # rotation: old token can't be reused
        return await self.issue_tokens(subject, role)

    async def logout(self, refresh_token: str) -> None:
        try:
            payload = decode_token(refresh_token, expected_type="refresh")
        except TokenError:
            return  # already unusable
        jti = payload.get("jti")
        if jti:
            await refresh_store.revoke(jti)
