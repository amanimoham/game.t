"""TransactionAnalysisService — simulated, consent-gated spending insights.

Produces category-level breakdowns and *educational* recommendations only.
No raw transactions, merchants, or sensitive banking details are exposed. The
numbers are deterministic per parent (stable across refreshes) but simulated.
"""
from __future__ import annotations

import hashlib
import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.banking_service import BankingConnectionService


class NotConnectedError(Exception):
    """Raised when insights are requested without an active consented connection."""


# Category keys → Arabic labels (kid/parent friendly).
CATEGORIES = [
    ("essentials", "الاحتياجات الأساسية"),
    ("entertainment", "المشتريات الترفيهية"),
    ("subscriptions", "الاشتراكات"),
    ("recurring", "المشتريات المتكررة"),
]


def _seed(parent_id: uuid.UUID) -> int:
    return int(hashlib.sha256(str(parent_id).encode()).hexdigest(), 16)


class TransactionAnalysisService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def analyze(self, parent_id: uuid.UUID) -> dict:
        if not await BankingConnectionService(self.db).is_connected(parent_id):
            raise NotConnectedError("Bank account not connected")

        seed = _seed(parent_id)
        # Base weights perturbed deterministically per parent.
        base = {"essentials": 0.45, "entertainment": 0.22, "subscriptions": 0.15, "recurring": 0.18}
        jitter = [(seed >> (i * 5)) % 10 for i in range(4)]  # 0..9 each
        weights = {}
        for (k, _), j in zip(CATEGORIES, jitter):
            weights[k] = base[k] * (0.8 + j / 25.0)
        total_w = sum(weights.values())
        monthly_total = Decimal(1200 + seed % 1400)  # simulated SAR-like total

        categories = []
        for key, label in CATEGORIES:
            pct = round(100 * weights[key] / total_w)
            amount = (monthly_total * Decimal(pct) / Decimal(100)).quantize(Decimal("1"))
            categories.append({"key": key, "label": label, "amount": int(amount), "pct": pct})

        ent = next(c for c in categories if c["key"] == "entertainment")["pct"]
        subs = next(c for c in categories if c["key"] == "subscriptions")["pct"]
        recurring = next(c for c in categories if c["key"] == "recurring")["pct"]

        recommendations = self._recommendations(ent, subs, recurring)

        return {
            "simulated": True,
            "monthly_total": int(monthly_total),
            "categories": categories,
            "recommendations": recommendations,
        }

    @staticmethod
    def _recommendations(entertainment_pct: int, subscriptions_pct: int, recurring_pct: int) -> list[str]:
        recs: list[str] = []
        if entertainment_pct >= 25:
            recs.append(
                "لاحظنا زيادة في المشتريات الترفيهية هذا الأسبوع — هل تريد تحدي الطفل لتأجيل بعض الرغبات؟"
            )
        potential = min(30, entertainment_pct + max(0, recurring_pct - 15))
        recs.append(
            f"الوصول للهدف يصبح أسرع بنسبة ~{potential}% عند تقليل المشتريات غير الضرورية."
        )
        if subscriptions_pct >= 18:
            recs.append("راجع الاشتراكات المتكررة — إلغاء اشتراك غير مستخدم يقرّب هدف الادخار.")
        recs.append("كافئ طفلك عند اتخاذه قراراً بتأجيل شراء — يعزّز عادة الادخار.")
        return recs
