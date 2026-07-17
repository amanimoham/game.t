"""Tunable constants for the decision/scoring engine.

Kept in one place so game designers can balance the game without touching
logic, and so the same numbers feed both the engine and (later) AI features.
"""
from __future__ import annotations

# The three skills the game measures and grows.
SKILLS: tuple[str, ...] = ("patience", "saving_awareness", "impulse_control")

# How much each monster archetype trains each skill (weights sum ~1.0 per monster).
MONSTER_SKILL_WEIGHTS: dict[str, dict[str, float]] = {
    "instant_reward": {"impulse_control": 0.6, "patience": 0.4, "saving_awareness": 0.0},
    "social_pressure": {"saving_awareness": 0.5, "impulse_control": 0.3, "patience": 0.2},
    "limited_offer": {"patience": 0.5, "saving_awareness": 0.3, "impulse_control": 0.2},
    "spending": {"saving_awareness": 0.6, "impulse_control": 0.4, "patience": 0.0},
}

# Which monster best trains a given (weak) skill — used by the AI monster selector.
SKILL_TO_MONSTER: dict[str, str] = {
    "impulse_control": "instant_reward",
    "saving_awareness": "spending",
    "patience": "limited_offer",
}

SKILL_GAIN: float = 12.0        # base added to a weighted skill on a correct choice
SKILL_PENALTY: float = 6.0      # base subtracted on an incorrect choice
IMPULSIVE_MS: int = 1500        # a WRONG choice faster than this reads as impulsive
DELIBERATE_MS: int = 4000       # a CORRECT choice slower than this earns a patience bonus

SKILL_MIN: float = 0.0
SKILL_MAX: float = 100.0
