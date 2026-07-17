from __future__ import annotations

from app.game_engine.engine import (
    DecisionInput,
    apply_skill_deltas,
    compute_progress_pct,
    evaluate_decision,
    is_level_complete,
)


def test_correct_choice_defeats_and_scores() -> None:
    out = evaluate_decision(
        DecisionInput("instant_reward", "wait", "wait", points=10, reaction_time_ms=2000)
    )
    assert out.correct and out.defeated
    assert out.score_change == 10
    # instant_reward trains impulse_control (0.6) and patience (0.4), positively.
    assert out.skill_deltas["impulse_control"] > 0
    assert out.skill_deltas["patience"] > 0


def test_wrong_choice_no_score_and_negative_deltas() -> None:
    out = evaluate_decision(
        DecisionInput("instant_reward", "wait", "buy", points=10, reaction_time_ms=5000)
    )
    assert not out.correct and not out.defeated
    assert out.score_change == 0
    assert out.skill_deltas["impulse_control"] < 0


def test_fast_wrong_choice_is_impulsive_extra_penalty() -> None:
    slow = evaluate_decision(
        DecisionInput("instant_reward", "wait", "buy", points=10, reaction_time_ms=5000)
    )
    fast = evaluate_decision(
        DecisionInput("instant_reward", "wait", "buy", points=10, reaction_time_ms=800)
    )
    assert fast.impulsive and not slow.impulsive
    # Impulsive path penalises impulse_control more.
    assert fast.skill_deltas["impulse_control"] < slow.skill_deltas["impulse_control"]


def test_deliberate_correct_gives_patience_bonus() -> None:
    quick = evaluate_decision(
        DecisionInput("limited_offer", "ignore", "ignore", points=10, reaction_time_ms=1000)
    )
    slow = evaluate_decision(
        DecisionInput("limited_offer", "ignore", "ignore", points=10, reaction_time_ms=6000)
    )
    assert slow.skill_deltas["patience"] > quick.skill_deltas["patience"]


def test_apply_skill_deltas_clamps() -> None:
    assert apply_skill_deltas({"patience": 98.0}, {"patience": 10.0})["patience"] == 100.0
    assert apply_skill_deltas({"patience": 3.0}, {"patience": -10.0})["patience"] == 0.0


def test_progress_pct() -> None:
    assert compute_progress_pct(0, 3) == 0
    assert compute_progress_pct(2, 3) == 67
    assert compute_progress_pct(3, 3) == 100
    assert compute_progress_pct(1, 0) == 0


def test_level_completion_gates() -> None:
    assert is_level_complete(20, 20, True, True)
    assert not is_level_complete(20, 20, True, False)   # final not beaten
    assert not is_level_complete(15, 20, True, True)     # score below threshold
    assert not is_level_complete(30, 20, False, True)    # a required monster left
