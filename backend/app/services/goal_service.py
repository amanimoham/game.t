"""GoalTrackingService — saving goals; progress ties to the child's real reward.

When a goal is linked to a child, current progress is derived from that child's
latest reward's unlocked amount (real data), not a stored guess.
"""
from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.banking import SavingGoal
from app.models.child import Child
from app.models.enums import GoalStatus
from app.models.reward import RewardOrder


class GoalError(Exception):
    pass


class GoalTrackingService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_goal(
        self,
        parent_id: uuid.UUID,
        title: str,
        target_amount: Decimal,
        child_id: uuid.UUID | None = None,
        target_date: date | None = None,
    ) -> SavingGoal:
        if child_id is not None:
            child = await self.db.get(Child, child_id)
            if child is None or child.parent_id != parent_id:
                raise GoalError("Child not found")
        goal = SavingGoal(
            parent_id=parent_id,
            child_id=child_id,
            title=title,
            target_amount=target_amount,
            target_date=target_date,
            status=GoalStatus.ACTIVE,
        )
        self.db.add(goal)
        await self.db.commit()
        await self.db.refresh(goal)
        return goal

    async def list_goals(self, parent_id: uuid.UUID) -> list[dict]:
        goals = (
            (
                await self.db.execute(
                    select(SavingGoal)
                    .where(SavingGoal.parent_id == parent_id)
                    .order_by(SavingGoal.created_at.desc())
                )
            )
            .scalars()
            .all()
        )
        out = []
        for g in goals:
            current = await self._current_amount(g)
            target = g.target_amount or Decimal("0")
            remaining = target - current
            if remaining < 0:
                remaining = Decimal("0")
            pct = int(min(100, round(100 * float(current) / float(target)))) if target > 0 else 0
            days = None
            if g.target_date is not None:
                days = (g.target_date - datetime.now(timezone.utc).date()).days
            out.append(
                {
                    "id": g.id,
                    "title": g.title,
                    "target_amount": target,
                    "current_amount": current,
                    "remaining_amount": remaining,
                    "currency": g.currency,
                    "progress_pct": pct,
                    "days_remaining": days,
                    "status": g.status.value,
                }
            )
        return out

    async def _current_amount(self, goal: SavingGoal) -> Decimal:
        """Derive live progress from the linked child's latest reward, else stored."""
        if goal.child_id is None:
            return goal.current_amount or Decimal("0")
        reward = (
            await self.db.execute(
                select(RewardOrder)
                .where(RewardOrder.child_id == goal.child_id)
                .order_by(RewardOrder.created_at.desc())
                .limit(1)
            )
        ).scalar_one_or_none()
        if reward is None:
            return goal.current_amount or Decimal("0")
        return reward.unlocked_amount or Decimal("0")
