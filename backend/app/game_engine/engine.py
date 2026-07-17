"""Pure decision/scoring engine — no I/O, fully unit-testable.

Given a child's choice against a challenge it returns whether the monster was
defeated, the game-score change, and per-skill deltas. It also computes
reward-unlock progress. Persistence and personalization live elsewhere.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.game_engine.constants import (
    DELIBERATE_MS,
    IMPULSIVE_MS,
    MONSTER_SKILL_WEIGHTS,
    SKILL_GAIN,
    SKILL_MAX,
    SKILL_MIN,
    SKILL_PENALTY,
    SKILLS,
)


@dataclass(frozen=True)
class DecisionInput:
    monster_code: str
    correct_behavior: str          # e.g. "wait" | "refuse" | "ignore"
    selected_kind: str             # the chosen option's kind
    points: int                    # challenge points on success
    reaction_time_ms: int | None = None
    attempt: int = 1


@dataclass(frozen=True)
class DecisionOutcome:
    correct: bool
    defeated: bool
    score_change: int
    impulsive: bool
    skill_deltas: dict[str, float] = field(default_factory=dict)


def evaluate_decision(inp: DecisionInput) -> DecisionOutcome:
    """Evaluate one choice. For the MVP a correct choice defeats the monster."""
    weights = MONSTER_SKILL_WEIGHTS.get(inp.monster_code, {})
    correct = inp.selected_kind == inp.correct_behavior

    deltas: dict[str, float] = {skill: 0.0 for skill in SKILLS}
    if correct:
        score_change = inp.points
        for skill, weight in weights.items():
            deltas[skill] += SKILL_GAIN * weight
    else:
        score_change = 0
        for skill, weight in weights.items():
            deltas[skill] -= SKILL_PENALTY * weight

    # Fast + wrong == impulsive: extra impulse-control penalty and a signal for AI.
    impulsive = (
        not correct
        and inp.reaction_time_ms is not None
        and inp.reaction_time_ms < IMPULSIVE_MS
    )
    if impulsive:
        deltas["impulse_control"] -= SKILL_PENALTY * 0.5

    # Slow + correct == deliberate patience: small bonus.
    if (
        correct
        and inp.reaction_time_ms is not None
        and inp.reaction_time_ms > DELIBERATE_MS
    ):
        deltas["patience"] += SKILL_GAIN * 0.2

    # Drop zero deltas for a clean payload.
    deltas = {k: round(v, 2) for k, v in deltas.items() if abs(v) > 1e-9}

    return DecisionOutcome(
        correct=correct,
        defeated=correct,
        score_change=score_change,
        impulsive=impulsive,
        skill_deltas=deltas,
    )


def apply_skill_deltas(
    current: dict[str, float], deltas: dict[str, float]
) -> dict[str, float]:
    """Apply deltas and clamp every skill to [SKILL_MIN, SKILL_MAX]."""
    updated = dict(current)
    for skill, delta in deltas.items():
        value = updated.get(skill, 0.0) + delta
        updated[skill] = max(SKILL_MIN, min(SKILL_MAX, round(value, 2)))
    return updated


def compute_progress_pct(defeated_count: int, total_challenges: int) -> int:
    """Percent of the journey completed (0..100)."""
    if total_challenges <= 0:
        return 0
    pct = round(100 * defeated_count / total_challenges)
    return max(0, min(100, pct))


def is_level_complete(
    total_score: int,
    required_score: int,
    all_required_defeated: bool,
    final_defeated: bool,
) -> bool:
    """A level (and thus the unlock) is complete only when every gate passes."""
    return all_required_defeated and final_defeated and total_score >= required_score
