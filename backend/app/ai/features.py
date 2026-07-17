"""Feature extraction — the ML-ready bridge.

Turns raw decision history + profile into a flat feature dict. This is exactly
the vector a future model would train on; today it feeds the rule engine and is
logged so we accumulate a labelled training set from day one.
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from app.ai.schemas import ChildContext
from app.game_engine.constants import SKILLS


def build_features(
    skills: dict[str, float],
    recent_decisions: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    """`recent_decisions` items: {correct: bool, reaction_time_ms: int|None,
    monster_code: str, impulsive: bool}. Ordered oldest -> newest."""
    total = len(recent_decisions)
    corrects = [bool(d.get("correct")) for d in recent_decisions]
    reactions = [
        d["reaction_time_ms"]
        for d in recent_decisions
        if d.get("reaction_time_ms") is not None
    ]

    resist_rate = (sum(corrects) / total) if total else 0.0
    avg_reaction = (sum(reactions) / len(reactions)) if reactions else None

    # Trailing streak of correct decisions.
    streak = 0
    for correct in reversed(corrects):
        if correct:
            streak += 1
        else:
            break

    last = recent_decisions[-1] if recent_decisions else {}

    features: dict[str, Any] = {
        f"skill_{s}": float(skills.get(s, 0.0)) for s in SKILLS
    }
    features.update(
        {
            "resist_rate": round(resist_rate, 4),
            "avg_reaction_ms": avg_reaction,
            "streak": streak,
            "total_decisions": total,
            "last_correct": bool(last.get("correct")) if last else None,
            "last_impulsive": bool(last.get("impulsive")) if last else False,
        }
    )
    return features


def context_from_features(
    skills: dict[str, float], features: dict[str, Any]
) -> ChildContext:
    last_outcome = None
    if features.get("total_decisions"):
        last_outcome = "defeated" if features.get("last_correct") else "gave_in"
    return ChildContext(
        skills=skills,
        resist_rate=float(features.get("resist_rate", 0.0)),
        avg_reaction_ms=features.get("avg_reaction_ms"),
        streak=int(features.get("streak", 0)),
        last_outcome=last_outcome,
        last_impulsive=bool(features.get("last_impulsive", False)),
        total_decisions=int(features.get("total_decisions", 0)),
    )
