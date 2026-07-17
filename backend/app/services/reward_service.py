"""Reward escrow service: applies gradual unlock against the database.

Wraps the pure ``reward_math`` with persistence, immutable unlock events, an
audit trail, and status transitions. Auth/identity checks are enforced by the
API layer (Step: auth); this service assumes an authorized caller.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.models.enums import ActorType, RewardStatus
from app.models.reward import RewardOrder, RewardUnlockEvent
from app.services import reward_math


class RewardService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def apply_progress(
        self,
        order: RewardOrder,
        progress_pct: int,
        *,
        reason: str = "challenge_defeated",
        completed: bool = False,
    ) -> RewardUnlockEvent | None:
        """Release any newly-earned amount for a progress update.

        Idempotent: re-applying the same or a lower progress releases nothing.
        Returns the created unlock event, or None if nothing was released.
        """
        target = reward_math.unlocked_for_progress(order.amount, progress_pct)
        delta = reward_math.release_delta(order.unlocked_amount, target)

        # Always advance the visible progress (monotonic).
        order.progress_pct = max(order.progress_pct, max(0, min(100, progress_pct)))

        event: RewardUnlockEvent | None = None
        if delta > 0:
            order.unlocked_amount = target
            event = RewardUnlockEvent(
                reward_order_id=order.id, amount=delta, reason=reason
            )
            self.db.add(event)
            if order.status == RewardStatus.LOCKED:
                order.status = RewardStatus.IN_PROGRESS

        if completed and progress_pct >= 100:
            order.status = RewardStatus.COMPLETED
            order.completed_at = datetime.now(timezone.utc)

        self.db.add(
            AuditLog(
                actor_type=ActorType.SYSTEM,
                action="reward.progress_applied",
                entity_type="reward_order",
                entity_id=order.id,
                event_metadata={
                    "progress_pct": order.progress_pct,
                    "released": str(delta),
                    "unlocked_amount": str(order.unlocked_amount),
                    "reason": reason,
                },
            )
        )
        await self.db.flush()
        return event

    async def get_order(self, order_id) -> RewardOrder | None:
        result = await self.db.execute(
            select(RewardOrder).where(RewardOrder.id == order_id)
        )
        return result.scalar_one_or_none()
