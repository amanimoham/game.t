from __future__ import annotations

from app.ai.features import build_features, context_from_features
from app.ai.schemas import ChildContext
from app.ai.strategies import (
    RuleDifficultyAdjuster,
    RuleEncouragementSelector,
    RuleMonsterSelector,
    RuleSuccessPredictor,
)

AVAILABLE = ["instant_reward", "social_pressure", "limited_offer", "spending"]


def test_monster_selector_targets_weakest_skill() -> None:
    ctx = ChildContext(skills={"patience": 90, "saving_awareness": 80, "impulse_control": 20})
    assert RuleMonsterSelector().select(ctx, AVAILABLE) == "instant_reward"

    ctx2 = ChildContext(skills={"patience": 10, "saving_awareness": 80, "impulse_control": 70})
    assert RuleMonsterSelector().select(ctx2, AVAILABLE) == "limited_offer"


def test_difficulty_stays_in_bounds_and_reacts() -> None:
    adj = RuleDifficultyAdjuster()
    easy = adj.adjust(ChildContext(skills={}, resist_rate=0.2, total_decisions=5))
    hard = adj.adjust(ChildContext(skills={}, resist_rate=0.95, total_decisions=5))
    assert 1 <= easy <= 5 and 1 <= hard <= 5
    assert hard > easy


def test_encouragement_is_supportive_per_context() -> None:
    sel = RuleEncouragementSelector()
    assert sel.select(ChildContext(skills={})).key == "welcome"
    assert sel.select(
        ChildContext(skills={}, last_outcome="defeated", streak=3)
    ).key == "defeated_streak"
    assert sel.select(
        ChildContext(skills={}, last_outcome="gave_in", last_impulsive=True)
    ).key == "gave_in_impulse"


def test_success_predictor_range_and_labels() -> None:
    pred = RuleSuccessPredictor()
    strong = pred.predict(
        ChildContext(skills={"patience": 90, "saving_awareness": 85, "impulse_control": 80}, resist_rate=0.9)
    )
    weak = pred.predict(
        ChildContext(skills={"patience": 10, "saving_awareness": 15, "impulse_control": 5}, resist_rate=0.1)
    )
    assert 0.0 <= weak.probability <= strong.probability <= 1.0
    assert strong.label == "on_track"
    assert weak.label == "at_risk"


def test_feature_extraction_and_roundtrip() -> None:
    decisions = [
        {"correct": True, "reaction_time_ms": 2000, "monster_code": "instant_reward", "impulsive": False},
        {"correct": False, "reaction_time_ms": 800, "monster_code": "social_pressure", "impulsive": True},
        {"correct": True, "reaction_time_ms": 3000, "monster_code": "limited_offer", "impulsive": False},
    ]
    skills = {"patience": 50, "saving_awareness": 40, "impulse_control": 30}
    feats = build_features(skills, decisions)
    assert feats["total_decisions"] == 3
    assert abs(feats["resist_rate"] - 2 / 3) < 1e-3   # resist_rate rounded to 4dp
    assert feats["streak"] == 1               # last decision correct, prior wrong
    assert feats["skill_patience"] == 50.0

    ctx = context_from_features(skills, feats)
    assert ctx.last_outcome == "defeated"     # last decision was correct
    assert ctx.total_decisions == 3
