"""Builds the ML training dataset from accumulated gameplay.

Emits one row per child: the AI features we log during play + a label
(did the child eventually complete a reward journey). This is exactly the
matrix a future model trains on to predict completion probability — the same
`build_features` contract the live rule engine already consumes.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.features import build_features
from app.game_engine.constants import IMPULSIVE_MS
from app.models.analytics import ChildDecision, ChildProfile
from app.models.child import Child
from app.models.enums import RewardStatus
from app.models.reward import RewardOrder


async def export_completion_dataset(db: AsyncSession) -> list[dict[str, Any]]:
    children = (await db.execute(select(Child))).scalars().all()
    rows: list[dict[str, Any]] = []

    for child in children:
        decisions = (
            (
                await db.execute(
                    select(ChildDecision)
                    .where(ChildDecision.child_id == child.id)
                    .order_by(ChildDecision.created_at)
                )
            )
            .scalars()
            .all()
        )
        if not decisions:
            continue

        recent = [
            {
                "correct": d.score_change > 0,
                "reaction_time_ms": d.response_time,
                "impulsive": (
                    d.score_change <= 0
                    and d.response_time is not None
                    and d.response_time < IMPULSIVE_MS
                ),
            }
            for d in decisions
        ]

        profile = await db.get(ChildProfile, child.id)
        skills = {
            "patience": float(profile.patience_score) if profile else 0.0,
            "saving_awareness": float(profile.saving_awareness_score) if profile else 0.0,
            "impulse_control": float(profile.impulse_control_score) if profile else 0.0,
        }
        features = build_features(skills, recent)

        completed = (
            await db.execute(
                select(RewardOrder.id).where(
                    RewardOrder.child_id == child.id,
                    RewardOrder.status.in_(
                        [RewardStatus.COMPLETED, RewardStatus.DELIVERED]
                    ),
                )
            )
        ).first() is not None

        rows.append(
            {
                "child_id": str(child.id),
                "age_group": child.age_group.value,
                **features,
                "label_completed": int(completed),
            }
        )

    return rows
