"""Pure reward-unlock arithmetic (no I/O) — money-safe and fully testable.

Uses Decimal with explicit rounding; unlock is monotonic (never releases a
negative amount) so a stale/duplicate progress update cannot claw back funds.
"""
from __future__ import annotations

from decimal import ROUND_DOWN, Decimal

_CENTS = Decimal("0.01")


def quantize(value: Decimal) -> Decimal:
    return value.quantize(_CENTS, rounding=ROUND_DOWN)


def unlocked_for_progress(amount: Decimal, progress_pct: int) -> Decimal:
    """Amount that should be unlocked at a given progress percent (0..100)."""
    pct = max(0, min(100, progress_pct))
    if pct >= 100:
        return quantize(amount)  # full amount, exact
    return quantize(amount * Decimal(pct) / Decimal(100))


def release_delta(current_unlocked: Decimal, target_unlocked: Decimal) -> Decimal:
    """How much to release now = max(0, target - current). Never negative."""
    delta = target_unlocked - current_unlocked
    return delta if delta > 0 else Decimal("0.00")
