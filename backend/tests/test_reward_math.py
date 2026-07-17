from __future__ import annotations

from decimal import Decimal

from app.services.reward_math import (
    release_delta,
    unlocked_for_progress,
    quantize,
)


def test_unlocked_scales_with_progress() -> None:
    amount = Decimal("500.00")
    assert unlocked_for_progress(amount, 0) == Decimal("0.00")
    assert unlocked_for_progress(amount, 67) == Decimal("335.00")
    assert unlocked_for_progress(amount, 100) == Decimal("500.00")


def test_full_progress_is_exact_amount() -> None:
    # Odd amount must return exactly the full value at 100%, no rounding loss.
    assert unlocked_for_progress(Decimal("333.33"), 100) == Decimal("333.33")


def test_progress_is_clamped() -> None:
    assert unlocked_for_progress(Decimal("100.00"), -20) == Decimal("0.00")
    assert unlocked_for_progress(Decimal("100.00"), 250) == Decimal("100.00")


def test_release_delta_never_negative() -> None:
    # Stale/duplicate progress must not claw back funds.
    assert release_delta(Decimal("335.00"), Decimal("335.00")) == Decimal("0.00")
    assert release_delta(Decimal("335.00"), Decimal("200.00")) == Decimal("0.00")
    assert release_delta(Decimal("200.00"), Decimal("335.00")) == Decimal("135.00")


def test_quantize_rounds_down_to_cents() -> None:
    assert quantize(Decimal("10.999")) == Decimal("10.99")
