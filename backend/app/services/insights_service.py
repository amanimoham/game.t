"""Parent-dashboard insights for a child (ownership-checked)."""
from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.features import build_features, context_from_features
from app.ai.strategies import success_predictor
from app.game_engine.engine import apply_skill_deltas
from app.models.analytics import BehaviorEvent, ChildDecision
from app.models.child import Child
from app.models.game import Challenge, MonsterType
from app.services.game_service import GameService
from app.services.reward_order_service import RewardOrderService


class InsightsError(Exception):
    pass


class InsightsService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def child_overview(self, parent_id: uuid.UUID, child_id: uuid.UUID) -> dict:
        child = await self.db.get(Child, child_id)
        if child is None or child.parent_id != parent_id or not child.is_active:
            raise InsightsError("Child not found")

        game = GameService(self.db)
        skills = await game._skills(child_id)
        recent = await game._recent_decisions(child_id, limit=500)
        features = build_features(skills, recent)
        ctx = context_from_features(skills, features)
        prediction = success_predictor.predict(ctx)

        defeated_monsters = await self._defeated_monster_names(child_id)
        rewards = await RewardOrderService(self.db).list_for_child(child_id)

        return {
            "child": child,
            "skills": skills,
            "total_decisions": features["total_decisions"],
            "resist_rate": features["resist_rate"],
            "success_prediction": {
                "probability": prediction.probability,
                "label": prediction.label,
            },
            "defeated_monsters": defeated_monsters,
            "rewards": rewards,
        }

    async def child_timeline(self, parent_id: uuid.UUID, child_id: uuid.UUID) -> list[dict]:
        """Replay decisions to chart skill growth over time (parent dashboard)."""
        child = await self.db.get(Child, child_id)
        if child is None or child.parent_id != parent_id or not child.is_active:
            raise InsightsError("Child not found")

        code_map = {
            row[0]: row[1].value
            for row in (await self.db.execute(select(MonsterType.id, MonsterType.code))).all()
        }
        events = (
            (
                await self.db.execute(
                    select(BehaviorEvent)
                    .where(
                        BehaviorEvent.child_id == child_id,
                        BehaviorEvent.event_name == "decision",
                    )
                    .order_by(BehaviorEvent.created_at)
                )
            )
            .scalars()
            .all()
        )

        skills = {"patience": 0.0, "saving_awareness": 0.0, "impulse_control": 0.0}
        points: list[dict] = []
        for step, event in enumerate(events, start=1):
            data = event.event_data or {}
            skills = apply_skill_deltas(skills, data.get("skill_deltas", {}))
            points.append(
                {
                    "step": step,
                    "correct": bool(data.get("correct")),
                    "monster_code": code_map.get(event.monster_type_id),
                    "patience": skills["patience"],
                    "saving_awareness": skills["saving_awareness"],
                    "impulse_control": skills["impulse_control"],
                }
            )
        return points

    async def _defeated_monster_names(self, child_id: uuid.UUID) -> list[str]:
        rows = (
            await self.db.execute(
                select(MonsterType.name)
                .join(Challenge, Challenge.monster_type_id == MonsterType.id)
                .join(ChildDecision, ChildDecision.challenge_id == Challenge.id)
                .where(ChildDecision.child_id == child_id, ChildDecision.score_change > 0)
                .distinct()
            )
        ).scalars().all()
        return list(rows)
