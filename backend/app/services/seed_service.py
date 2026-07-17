"""Reusable content seeding (used by scripts/seed.py and the integration test)."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.game_engine.seed_data import CHALLENGES, LEVEL, MONSTER_TYPES
from app.models.enums import MonsterCode
from app.models.game import Challenge, Level, MonsterType


async def seed_content(db: AsyncSession) -> None:
    """Idempotent: monster types (by code) + one level with its challenges."""
    code_to_id: dict[str, object] = {}
    for spec in MONSTER_TYPES:
        existing = await db.execute(
            select(MonsterType).where(MonsterType.code == MonsterCode(spec["code"]))
        )
        monster = existing.scalar_one_or_none()
        if monster is None:
            monster = MonsterType(
                code=MonsterCode(spec["code"]),
                name=spec["name"],
                description=spec["description"],
                effect=spec["effect"],
                base_difficulty=spec["base_difficulty"],
            )
            db.add(monster)
            await db.flush()
        code_to_id[spec["code"]] = monster.id

    existing_level = await db.execute(select(Level).where(Level.name == LEVEL["name"]))
    if existing_level.scalar_one_or_none() is None:
        level = Level(**LEVEL)
        db.add(level)
        await db.flush()
        for spec in CHALLENGES:
            db.add(
                Challenge(
                    level_id=level.id,
                    monster_type_id=code_to_id[spec["monster_code"]],
                    scenario=spec["scenario"],
                    choices=spec["choices"],
                    correct_behavior=spec["correct_behavior"],
                    points=spec["points"],
                    is_final=spec["is_final"],
                    order_index=spec["order_index"],
                )
            )

    await db.commit()
