"""Vertical-slice content: 4 monster types (catalog) + 1 level + 3 challenges.

Pure data — the seed runner (scripts/seed.py) inserts it. Kept declarative so
designers can extend content without touching insert logic.
"""
from __future__ import annotations

MONSTER_TYPES = [
    {
        "code": "instant_reward",
        "name": "وحش الشراء السريع",
        "description": "يغريك أن تشتري فوراً دون تفكير.",
        "effect": {"grows_on": "impulse", "teaches": "impulse_control"},
        "base_difficulty": 1,
    },
    {
        "code": "social_pressure",
        "name": "وحش ضغط الأصدقاء",
        "description": "يقنعك أن تشتري لأن الجميع اشترى.",
        "effect": {"grows_on": "conformity", "teaches": "saving_awareness"},
        "base_difficulty": 2,
    },
    {
        "code": "limited_offer",
        "name": "وحش العروض الوهمية",
        "description": "يخيفك بعدّاد 'بقي القليل!' ليجعلك تتسرّع.",
        "effect": {"grows_on": "urgency", "teaches": "patience"},
        "base_difficulty": 2,
    },
    {
        "code": "spending",
        "name": "وحش الإنفاق",
        "description": "يدفعك لإنفاق كل ما تملك.",
        "effect": {"grows_on": "spending", "teaches": "saving_awareness"},
        "base_difficulty": 3,
    },
]

# The playable slice: one level, three challenges (the 3rd is the final boss).
LEVEL = {
    "name": "رحلة الكنز — المرحلة 1",
    "difficulty": 1,
    "required_score": 20,
    "order_index": 1,
    "is_required": True,
}

CHALLENGES = [
    {
        "monster_code": "instant_reward",
        "scenario": "لعبة لامعة بـ 50 نقطة! زر أحمر يقول: اشترِ الآن!",
        "choices": [
            {"key": "a", "label": "أشتري الآن! 🤩", "kind": "buy"},
            {"key": "b", "label": "أنتظر وأفكّر 🤔", "kind": "wait"},
        ],
        "correct_behavior": "wait",
        "points": 10,
        "is_final": False,
        "order_index": 1,
    },
    {
        "monster_code": "social_pressure",
        "scenario": "كل أصدقائك اشتروا السكين الجديد في اللعبة. يقولون: اشترِ مثلنا!",
        "choices": [
            {"key": "a", "label": "أشتري مثلهم 😅", "kind": "buy"},
            {"key": "b", "label": "أقرّر بنفسي وأرفض 🛡️", "kind": "refuse"},
        ],
        "correct_behavior": "refuse",
        "points": 10,
        "is_final": False,
        "order_index": 2,
    },
    {
        "monster_code": "limited_offer",
        "scenario": "عدّاد يومض: 'بقي دقيقتان فقط! العرض ينتهي!' هل تتسرّع؟",
        "choices": [
            {"key": "a", "label": "أسرع قبل أن ينتهي! ⏰", "kind": "buy"},
            {"key": "b", "label": "أتجاهل العدّاد الوهمي 😌", "kind": "ignore"},
        ],
        "correct_behavior": "ignore",
        "points": 10,
        "is_final": True,
        "order_index": 3,
    },
]
