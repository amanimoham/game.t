"""Child profiles: creation, PIN management, PIN authentication."""
from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analytics import ChildProfile
from app.models.child import Child
from app.models.enums import AgeGroup
from app.security.hashing import hash_secret, verify_secret


class ChildError(Exception):
    """Domain error for child operations (mapped to 400/404 by the API)."""


class ChildService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_child(
        self, parent_id: uuid.UUID, nickname: str, age_group: AgeGroup
    ) -> Child:
        child = Child(parent_id=parent_id, nickname=nickname, age_group=age_group, is_active=True)
        self.db.add(child)
        await self.db.flush()
        # Start every child with a zeroed skill profile.
        self.db.add(ChildProfile(child_id=child.id))
        await self.db.commit()
        await self.db.refresh(child)
        return child

    async def list_children(self, parent_id: uuid.UUID) -> list[Child]:
        result = await self.db.execute(
            select(Child).where(Child.parent_id == parent_id, Child.is_active.is_(True))
        )
        return list(result.scalars().all())

    async def _owned_child(self, parent_id: uuid.UUID, child_id: uuid.UUID) -> Child:
        child = await self.db.get(Child, child_id)
        if child is None or child.parent_id != parent_id or not child.is_active:
            raise ChildError("Child not found")
        return child

    async def set_pin(self, parent_id: uuid.UUID, child_id: uuid.UUID, pin: str) -> None:
        child = await self._owned_child(parent_id, child_id)
        child.pin_hash = hash_secret(pin)
        await self.db.commit()

    async def authenticate_child(
        self, parent_id: uuid.UUID, child_id: uuid.UUID, pin: str
    ) -> Child:
        child = await self._owned_child(parent_id, child_id)
        if not verify_secret(pin, child.pin_hash):
            raise ChildError("Invalid PIN")
        return child
