"""Reward order creation (simulated funding) + lookup.

On creation we snapshot the *current* required content into ``unlock_criteria``
so an in-flight order is immune to later content changes.
"""
from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.models.child import Child
from app.models.enums import ActorType, RewardStatus, RewardType
from app.models.game import Challenge, Level
from app.models.reward import RewardOrder


class RewardOrderError(Exception):
    pass


class RewardOrderService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def _snapshot_criteria(self) -> dict:
        """Required levels + their challenge counts + minimum score."""
        levels = (
            (await self.db.execute(select(Level).where(Level.is_required.is_(True))))
            .scalars()
            .all()
        )
        level_ids = [str(level.id) for level in levels]
        min_score = sum(level.required_score for level in levels)
        total_challenges = 0
        if levels:
            total_challenges = (
                await self.db.execute(
                    select(func.count(Challenge.id)).where(
                        Challenge.level_id.in_([level.id for level in levels])
                    )
                )
            ).scalar_one()
        return {
            "level_ids": level_ids,
            "min_score": int(min_score),
            "total_challenges": int(total_challenges),
            "require_final": True,
        }

    async def create_order(
        self,
        parent_id: uuid.UUID,
        child_id: uuid.UUID,
        amount: Decimal,
        reward_type: RewardType = RewardType.ROBUX,
    ) -> RewardOrder:
        child = await self.db.get(Child, child_id)
        if child is None or child.parent_id != parent_id:
            raise RewardOrderError("Child not found")

        order = RewardOrder(
            parent_id=parent_id,
            child_id=child_id,
            reward_type=reward_type,
            amount=amount,
            status=RewardStatus.LOCKED,  # simulated funding → locked immediately
            unlocked_amount=Decimal("0.00"),
            progress_pct=0,
            unlock_criteria=await self._snapshot_criteria(),
        )
        self.db.add(order)
        await self.db.flush()
        self.db.add(
            AuditLog(
                actor_type=ActorType.PARENT,
                actor_id=parent_id,
                action="reward.created_and_funded",
                entity_type="reward_order",
                entity_id=order.id,
                event_metadata={"amount": str(amount), "reward_type": reward_type.value},
            )
        )
        await self.db.commit()
        await self.db.refresh(order)
        return order

    async def get_order(self, order_id: uuid.UUID) -> RewardOrder | None:
        return await self.db.get(RewardOrder, order_id)

    async def active_order_for_child(self, child_id: uuid.UUID) -> RewardOrder | None:
        result = await self.db.execute(
            select(RewardOrder)
            .where(
                RewardOrder.child_id == child_id,
                RewardOrder.status.in_([RewardStatus.LOCKED, RewardStatus.IN_PROGRESS]),
            )
            .order_by(RewardOrder.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def list_for_child(self, child_id: uuid.UUID) -> list[RewardOrder]:
        result = await self.db.execute(
            select(RewardOrder)
            .where(RewardOrder.child_id == child_id)
            .order_by(RewardOrder.created_at.desc())
        )
        return list(result.scalars().all())
