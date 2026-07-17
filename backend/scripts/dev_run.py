"""Zero-dependency local runner: embedded Postgres + in-process fakeredis.

Runs the full API on http://localhost:8000 WITHOUT Docker — handy for local
demos. Not for production (use docker-compose / Render there).

    python -m scripts.dev_run
"""
from __future__ import annotations

import asyncio
import os
import sys
import tempfile

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import pgserver  # noqa: E402

# 1) start embedded Postgres and point the app at it BEFORE importing app config
_data_dir = os.path.join(tempfile.gettempdir(), "muharabat_pgdata")
os.makedirs(_data_dir, exist_ok=True)
_server = pgserver.get_server(_data_dir)
os.environ["DATABASE_URL"] = _server.get_uri()

# 2) back the refresh-token store with in-process fakeredis
import fakeredis.aioredis  # noqa: E402

import app.security.redis_client as redis_client  # noqa: E402

redis_client._client = fakeredis.aioredis.FakeRedis(decode_responses=True)

# 3) create schema + seed content
import app.models  # noqa: E402,F401
from app.database.base import Base  # noqa: E402
from app.database.session import AsyncSessionLocal, engine  # noqa: E402
from app.services.seed_service import seed_content  # noqa: E402


async def _prepare() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as db:
        await seed_content(db)
    # Dispose so no pooled connections carry over to uvicorn's (different) loop.
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(_prepare())
    import uvicorn  # noqa: E402
    from app.main import app  # noqa: E402

    print(">>> DEV backend ready on http://localhost:8000 (embedded PG + fakeredis)")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
