"""Core gameplay orchestration: ties the pure engine + AI + persistence + reward.

This is where a child's choice becomes: a recorded decision, a telemetry event,
updated skills, reward progress, and an AI-chosen encouragement + next step.
"""
from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.features import build_features, context_from_features
from app.ai.strategies import (
    difficulty_adjuster,
    encouragement_selector,
    monster_selector,
    success_predictor,
)
from app.game_engine.constants import IMPULSIVE_MS, SKILLS
from app.game_engine.engine import (
    DecisionInput,
    apply_skill_deltas,
    compute_progress_pct,
    evaluate_decision,
    is_level_complete,
)
from app.models.analytics import BehaviorEvent, ChildDecision, ChildProfile
from app.models.child import Child
from app.models.game import Challenge, GameSession, Level, MonsterType
from app.models.enums import SessionStatus
from app.services.reward_order_service import RewardOrderService
from app.services.reward_service import RewardService

_SKILL_FIELD = {
    "patience": "patience_score",
    "saving_awareness": "saving_awareness_score",
    "impulse_control": "impulse_control_score",
}


class GameError(Exception):
    pass


class GameService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ---------- content ----------
    async def get_levels(self) -> list[dict]:
        levels = (
            (await self.db.execute(select(Level).order_by(Level.order_index)))
            .scalars()
            .all()
        )
        codes = await self._monster_code_map()
        out: list[dict] = []
        for level in levels:
            challenges = (
                (
                    await self.db.execute(
                        select(Challenge)
                        .where(Challenge.level_id == level.id)
                        .order_by(Challenge.order_index)
                    )
                )
                .scalars()
                .all()
            )
            out.append(
                {
                    "id": level.id,
                    "name": level.name,
                    "difficulty": level.difficulty,
                    "required_score": level.required_score,
                    "order_index": level.order_index,
                    "challenges": [
                        {
                            "id": c.id,
                            "scenario": c.scenario,
                            "choices": c.choices,
                            "points": c.points,
                            "is_final": c.is_final,
                            "order_index": c.order_index,
                            "monster_code": codes.get(c.monster_type_id),
                        }
                        for c in challenges
                    ],
                }
            )
        return out

    # ---------- session ----------
    async def start_session(self, child: Child) -> dict:
        session = GameSession(child_id=child.id, status=SessionStatus.ACTIVE)
        self.db.add(session)
        await self.db.flush()

        skills = await self._skills(child.id)
        ctx = context_from_features(skills, build_features(skills, []))
        available = list((await self._monster_code_map()).values())
        encouragement = encouragement_selector.select(ctx)
        await self.db.commit()
        return {
            "session_id": session.id,
            "encouragement": encouragement.message,
            "skills": skills,
            "suggested_monster": monster_selector.select(ctx, available) if available else "",
            "difficulty": difficulty_adjuster.adjust(ctx),
        }

    # ---------- the core loop ----------
    async def submit_decision(
        self,
        child: Child,
        session_id: uuid.UUID,
        challenge_id: uuid.UUID,
        choice_key: str,
        reaction_time_ms: int | None,
    ) -> dict:
        session = await self.db.get(GameSession, session_id)
        if session is None or session.child_id != child.id:
            raise GameError("Session not found")
        if session.status != SessionStatus.ACTIVE:
            raise GameError("Session is not active")

        challenge = await self.db.get(Challenge, challenge_id)
        if challenge is None:
            raise GameError("Challenge not found")
        monster = await self.db.get(MonsterType, challenge.monster_type_id)
        monster_code = monster.code.value if monster else ""

        selected_kind = self._choice_kind(challenge.choices, choice_key)
        if selected_kind is None:
            raise GameError("Invalid choice")

        outcome = evaluate_decision(
            DecisionInput(
                monster_code=monster_code,
                correct_behavior=challenge.correct_behavior,
                selected_kind=selected_kind,
                points=challenge.points,
                reaction_time_ms=reaction_time_ms,
            )
        )

        # 1) record the decision + telemetry
        self.db.add(
            ChildDecision(
                child_id=child.id,
                challenge_id=challenge.id,
                session_id=session.id,
                selected_choice=choice_key,
                response_time=reaction_time_ms,
                score_change=outcome.score_change,
            )
        )
        self.db.add(
            BehaviorEvent(
                child_id=child.id,
                session_id=session.id,
                event_name="decision",
                level_id=challenge.level_id,
                monster_type_id=challenge.monster_type_id,
                event_data={
                    "choice_key": choice_key,
                    "kind": selected_kind,
                    "correct": outcome.correct,
                    "impulsive": outcome.impulsive,
                    "reaction_time_ms": reaction_time_ms,
                    "skill_deltas": outcome.skill_deltas,
                },
            )
        )
        # Flush so this decision is visible to the reward-progress query below
        # (the session runs with autoflush disabled).
        await self.db.flush()

        # 2) update skills
        skills = await self._skills(child.id)
        new_skills = apply_skill_deltas(skills, outcome.skill_deltas)
        await self._save_skills(child.id, new_skills)

        # 3) advance session pointer
        session.current_level_id = challenge.level_id

        # 4) reward progress
        reward_progress = await self._apply_reward_progress(child.id)

        await self.db.commit()

        # 5) AI: encouragement + next step + prediction (post-commit, read-only)
        recent = await self._recent_decisions(child.id)
        ctx = context_from_features(new_skills, build_features(new_skills, recent))
        available = list((await self._monster_code_map()).values())
        prediction = success_predictor.predict(ctx)

        return {
            "correct": outcome.correct,
            "defeated": outcome.defeated,
            "score_change": outcome.score_change,
            "skills": new_skills,
            "encouragement": encouragement_selector.select(ctx).message,
            "next_suggested_monster": monster_selector.select(ctx, available) if available else "",
            "difficulty": difficulty_adjuster.adjust(ctx),
            "success_prediction": {"probability": prediction.probability, "label": prediction.label},
            "reward_progress": reward_progress,
        }

    async def get_progress(self, child: Child) -> dict:
        skills = await self._skills(child.id)
        recent = await self._recent_decisions(child.id, limit=200)
        features = build_features(skills, recent)
        ctx = context_from_features(skills, features)
        prediction = success_predictor.predict(ctx)
        return {
            "skills": skills,
            "total_decisions": features["total_decisions"],
            "resist_rate": features["resist_rate"],
            "success_prediction": {"probability": prediction.probability, "label": prediction.label},
        }

    # ---------- helpers ----------
    async def _monster_code_map(self) -> dict[uuid.UUID, str]:
        rows = (await self.db.execute(select(MonsterType.id, MonsterType.code))).all()
        return {row[0]: row[1].value for row in rows}

    @staticmethod
    def _choice_kind(choices: list, key: str) -> str | None:
        for choice in choices or []:
            if choice.get("key") == key:
                return choice.get("kind")
        return None

    async def _skills(self, child_id: uuid.UUID) -> dict[str, float]:
        profile = await self.db.get(ChildProfile, child_id)
        if profile is None:
            profile = ChildProfile(child_id=child_id)
            self.db.add(profile)
            await self.db.flush()
        return {
            "patience": float(profile.patience_score),
            "saving_awareness": float(profile.saving_awareness_score),
            "impulse_control": float(profile.impulse_control_score),
        }

    async def _save_skills(self, child_id: uuid.UUID, skills: dict[str, float]) -> None:
        profile = await self.db.get(ChildProfile, child_id)
        for skill in SKILLS:
            setattr(profile, _SKILL_FIELD[skill], skills[skill])

    async def _recent_decisions(self, child_id: uuid.UUID, limit: int = 20) -> list[dict]:
        rows = (
            (
                await self.db.execute(
                    select(ChildDecision)
                    .where(ChildDecision.child_id == child_id)
                    .order_by(ChildDecision.created_at.desc())
                    .limit(limit)
                )
            )
            .scalars()
            .all()
        )
        rows = list(reversed(rows))  # oldest -> newest
        result = []
        for d in rows:
            correct = d.score_change > 0
            impulsive = (
                not correct
                and d.response_time is not None
                and d.response_time < IMPULSIVE_MS
            )
            result.append(
                {"correct": correct, "reaction_time_ms": d.response_time, "impulsive": impulsive}
            )
        return result

    async def _apply_reward_progress(self, child_id: uuid.UUID) -> dict | None:
        orders = RewardOrderService(self.db)
        order = await orders.active_order_for_child(child_id)
        if order is None:
            return None

        level_ids = self._criteria_level_ids(order.unlock_criteria)
        challenges = (
            (
                await self.db.execute(
                    select(Challenge).where(Challenge.level_id.in_(level_ids))
                )
            )
            .scalars()
            .all()
        ) if level_ids else []
        total = len(challenges)

        defeated_ids = set(
            (
                await self.db.execute(
                    select(ChildDecision.challenge_id)
                    .where(
                        ChildDecision.child_id == child_id,
                        ChildDecision.score_change > 0,
                    )
                    .distinct()
                )
            )
            .scalars()
            .all()
        )
        required_ids = {c.id for c in challenges}
        defeated_required = required_ids & defeated_ids
        defeated_count = len(defeated_required)
        final_defeated = any(c.is_final and c.id in defeated_ids for c in challenges)
        total_score = sum(c.points for c in challenges if c.id in defeated_ids)

        pct = compute_progress_pct(defeated_count, total)
        min_score = int((order.unlock_criteria or {}).get("min_score", 0))
        completed = is_level_complete(
            total_score, min_score, defeated_count == total and total > 0, final_defeated
        )

        await RewardService(self.db).apply_progress(order, pct, completed=completed)
        return {
            "reward_id": order.id,
            "progress_pct": order.progress_pct,
            "unlocked_amount": order.unlocked_amount,
            "amount": order.amount,
            "status": order.status.value,
        }

    @staticmethod
    def _criteria_level_ids(criteria: dict | None) -> list[uuid.UUID]:
        ids = (criteria or {}).get("level_ids", [])
        out = []
        for value in ids:
            try:
                out.append(uuid.UUID(str(value)))
            except (ValueError, TypeError):
                continue
        return out
