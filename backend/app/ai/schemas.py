"""Typed inputs/outputs for the AI strategy layer.

These dataclasses are the stable contract: the rule-based implementations
produce them today, and future ML models will produce the exact same shapes,
so call sites never change.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChildContext:
    """Everything a strategy may look at to make a decision."""

    skills: dict[str, float]              # patience / saving_awareness / impulse_control (0..100)
    resist_rate: float = 0.0              # fraction of recent decisions that were correct
    avg_reaction_ms: float | None = None
    streak: int = 0                       # trailing consecutive correct decisions
    last_outcome: str | None = None       # "defeated" | "gave_in" | None
    last_impulsive: bool = False
    total_decisions: int = 0


@dataclass(frozen=True)
class Encouragement:
    key: str
    message: str


@dataclass(frozen=True)
class SuccessPrediction:
    probability: float                    # 0..1
    label: str                            # "on_track" | "needs_support" | "at_risk"
