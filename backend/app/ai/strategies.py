"""Rule-based AI strategies (swap for ML later without touching call sites).

Four strategies mirror the product's AI roadmap:
  - MonsterSelector      -> pick the temptation that trains the weakest skill
  - DifficultyAdjuster   -> keep success in the ~70-80% "growth zone"
  - EncouragementSelector-> pick a supportive, non-shaming message
  - SuccessPredictor     -> estimate probability the child finishes the journey

Each is a Protocol with a default rule-based implementation. Later, an ML
implementation just needs to satisfy the same Protocol.
"""
from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.ai.schemas import ChildContext, Encouragement, SuccessPrediction
from app.game_engine.constants import SKILL_TO_MONSTER, SKILLS

# --- Supportive, never-shaming message catalog (Arabic, child-facing) ---
ENCOURAGEMENT_CATALOG: dict[str, str] = {
    "defeated_streak": "🔥 بطل! هزمت الوحش بذكاء. سلسلتك تكبر!",
    "defeated": "أحسنت! قرار موفّق ذكّرك بهدفك 👏",
    "gave_in_impulse": "خذ نفساً 🌬️ واسأل: هل أحتاجه فعلاً أم أرغبه فقط؟",
    "gave_in": "قريب جداً! تذكّر كنزك وحافظ على نقودك 🪙",
    "welcome": "لنبدأ المغامرة! كنزك بانتظارك خلف الوحوش ✨",
}


@runtime_checkable
class MonsterSelector(Protocol):
    def select(self, ctx: ChildContext, available: list[str]) -> str: ...


@runtime_checkable
class DifficultyAdjuster(Protocol):
    def adjust(self, ctx: ChildContext) -> int: ...


@runtime_checkable
class EncouragementSelector(Protocol):
    def select(self, ctx: ChildContext) -> Encouragement: ...


@runtime_checkable
class SuccessPredictor(Protocol):
    def predict(self, ctx: ChildContext) -> SuccessPrediction: ...


class RuleMonsterSelector:
    """Target the weakest skill; fall back to the first available monster."""

    def select(self, ctx: ChildContext, available: list[str]) -> str:
        if not available:
            raise ValueError("no monsters available to select")
        weakest = min(SKILLS, key=lambda s: ctx.skills.get(s, 0.0))
        preferred = SKILL_TO_MONSTER.get(weakest)
        if preferred in available:
            return preferred
        return available[0]


class RuleDifficultyAdjuster:
    """Nudge difficulty (1..5) toward a ~70-80% success rate."""

    def adjust(self, ctx: ChildContext) -> int:
        base = 3
        if ctx.total_decisions == 0:
            return base
        if ctx.resist_rate >= 0.8:
            base += 1
        elif ctx.resist_rate < 0.5:
            base -= 1
        # Very fast average reactions -> tolerate more challenge.
        if ctx.avg_reaction_ms is not None and ctx.avg_reaction_ms < 1200:
            base += 1
        return max(1, min(5, base))


class RuleEncouragementSelector:
    def select(self, ctx: ChildContext) -> Encouragement:
        if ctx.last_outcome is None:
            return Encouragement("welcome", ENCOURAGEMENT_CATALOG["welcome"])
        if ctx.last_outcome == "defeated":
            key = "defeated_streak" if ctx.streak >= 2 else "defeated"
        else:  # gave_in
            key = "gave_in_impulse" if ctx.last_impulsive else "gave_in"
        return Encouragement(key, ENCOURAGEMENT_CATALOG[key])


class RuleSuccessPredictor:
    """Blend average skill and recent resist-rate into a completion probability."""

    def predict(self, ctx: ChildContext) -> SuccessPrediction:
        mean_skill = sum(ctx.skills.get(s, 0.0) for s in SKILLS) / len(SKILLS)
        skill_norm = mean_skill / 100.0
        prob = 0.5 * skill_norm + 0.5 * ctx.resist_rate
        prob = max(0.0, min(1.0, round(prob, 4)))
        if prob >= 0.7:
            label = "on_track"
        elif prob >= 0.45:
            label = "needs_support"
        else:
            label = "at_risk"
        return SuccessPrediction(probability=prob, label=label)


# Default singletons wired throughout the app (replace with ML impls later).
monster_selector: MonsterSelector = RuleMonsterSelector()
difficulty_adjuster: DifficultyAdjuster = RuleDifficultyAdjuster()
encouragement_selector: EncouragementSelector = RuleEncouragementSelector()
success_predictor: SuccessPredictor = RuleSuccessPredictor()
