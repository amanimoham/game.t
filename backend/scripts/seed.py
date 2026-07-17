"""Seed runner for the vertical-slice content.

Usage (inside the api container or a configured venv):
    python -m scripts.seed
"""
from __future__ import annotations

import asyncio

from app.database.session import AsyncSessionLocal
from app.services.seed_service import seed_content


async def main() -> None:
    async with AsyncSessionLocal() as db:
        await seed_content(db)
    print("Seed complete: monster types + level + challenges.")


if __name__ == "__main__":
    asyncio.run(main())
