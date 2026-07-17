"""End-to-end flow against a REAL Postgres (embedded via pgserver) + fakeredis.

Exercises the whole vertical slice:
  register parent -> create child -> set PIN -> child-login ->
  create (locked) reward -> start session -> defeat 3 monsters ->
  reward unlocks gradually to 100% -> parent dashboard reflects it.

Skips automatically if pgserver can't start (e.g. unsupported platform).
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

pgserver = pytest.importorskip("pgserver")
fakeredis = pytest.importorskip("fakeredis")

BACKEND = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def pg_async_uri():
    data_dir = tempfile.mkdtemp(prefix="pgtest_")
    server = pgserver.get_server(data_dir)
    sync_uri = server.get_uri()  # postgresql://postgres:@127.0.0.1:PORT/postgres
    # Run the real migration chain against it (also validates start.sh's step).
    env = dict(os.environ, DATABASE_URL=sync_uri)
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=str(BACKEND), env=env, check=True, capture_output=True,
    )
    yield sync_uri.replace("postgresql://", "postgresql+asyncpg://", 1)
    server.cleanup()


@pytest_asyncio.fixture
async def client(pg_async_uri):
    import app.security.redis_client as redis_client
    from app.database.session import get_db
    from app.main import app
    from app.services.seed_service import seed_content

    redis_client._client = fakeredis.aioredis.FakeRedis(decode_responses=True)

    engine = create_async_engine(pg_async_uri, poolclass=NullPool)
    # Mirror production session settings (autoflush disabled) so tests exercise
    # the same flush semantics as the real app.
    Session = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)

    async with Session() as db:
        await seed_content(db)

    async def _override_get_db():
        async with Session() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
    await engine.dispose()


async def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_full_journey_unlocks_reward(client: AsyncClient, pg_async_uri) -> None:
    # 1) parent registers
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": "parent@example.com", "password": "supersecret1"},
    )
    assert r.status_code == 201, r.text
    parent_h = await _auth_headers(r.json()["access_token"])

    # 2) create child
    r = await client.post(
        "/api/v1/children",
        headers=parent_h,
        json={"nickname": "Sami", "age_group": "8-10"},
    )
    assert r.status_code == 201, r.text
    child_id = r.json()["id"]

    # 3) set PIN
    r = await client.put(
        f"/api/v1/children/{child_id}/pin", headers=parent_h, json={"pin": "1234"}
    )
    assert r.status_code == 200, r.text

    # 4) child-login (parent hands over)
    r = await client.post(
        "/api/v1/auth/child-login",
        headers=parent_h,
        json={"child_id": child_id, "pin": "1234"},
    )
    assert r.status_code == 200, r.text
    child_h = await _auth_headers(r.json()["access_token"])

    # 5) parent funds a locked reward
    r = await client.post(
        "/api/v1/rewards",
        headers=parent_h,
        json={"child_id": child_id, "amount": "500.00", "reward_type": "robux"},
    )
    assert r.status_code == 201, r.text
    reward = r.json()
    reward_id = reward["id"]
    assert reward["status"] == "locked"
    assert reward["progress_pct"] == 0

    # 6) child reads levels
    r = await client.get("/api/v1/game/levels", headers=child_h)
    assert r.status_code == 200, r.text
    levels = r.json()
    assert len(levels) == 1
    challenges = sorted(levels[0]["challenges"], key=lambda c: c["order_index"])
    assert len(challenges) == 3

    # 7) start a session
    r = await client.post("/api/v1/game/sessions", headers=child_h)
    assert r.status_code == 200, r.text
    session_id = r.json()["session_id"]
    assert r.json()["encouragement"]  # welcome message present

    # 8) defeat all three monsters with the correct choice ("b")
    progress_seen = []
    for idx, ch in enumerate(challenges):
        r = await client.post(
            f"/api/v1/game/sessions/{session_id}/decisions",
            headers=child_h,
            json={"challenge_id": ch["id"], "choice_key": "b", "reaction_time_ms": 3000},
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["correct"] and body["defeated"]
        progress_seen.append(body["reward_progress"]["progress_pct"])

    # progress climbed and ended fully unlocked
    assert progress_seen[0] == 33
    assert progress_seen[1] == 67
    assert progress_seen[2] == 100

    # 9) parent sees a completed, fully-unlocked reward
    r = await client.get(f"/api/v1/rewards/{reward_id}", headers=parent_h)
    assert r.status_code == 200, r.text
    final = r.json()
    assert final["status"] == "completed"
    assert final["progress_pct"] == 100
    assert float(final["unlocked_amount"]) == 500.0

    # 10) dashboard reflects learning
    r = await client.get(f"/api/v1/dashboard/children/{child_id}", headers=parent_h)
    assert r.status_code == 200, r.text
    insights = r.json()
    assert len(insights["defeated_monsters"]) == 3
    assert insights["total_decisions"] == 3
    assert insights["resist_rate"] == 1.0
    # skills grew above zero
    assert insights["skills"]["impulse_control"] > 0
    assert insights["success_prediction"]["probability"] > 0

    # 11) P3: skill-growth timeline (3 points, non-decreasing impulse_control)
    r = await client.get(f"/api/v1/dashboard/children/{child_id}/timeline", headers=parent_h)
    assert r.status_code == 200, r.text
    timeline = r.json()
    assert len(timeline) == 3
    assert timeline[-1]["impulse_control"] >= timeline[0]["impulse_control"]

    # 12) P3: training dataset export yields a labelled row for this child
    from sqlalchemy.ext.asyncio import async_sessionmaker as _sm
    from app.services.training_data_service import export_completion_dataset

    eng = create_async_engine(pg_async_uri, poolclass=NullPool)
    async with _sm(eng, expire_on_commit=False)() as s:
        rows = await export_completion_dataset(s)
    await eng.dispose()
    mine = [row for row in rows if row["child_id"] == child_id]
    assert mine, "child not in training dataset"
    assert mine[0]["label_completed"] == 1
    assert mine[0]["total_decisions"] == 3


@pytest.mark.asyncio
async def test_open_banking_flow(client: AsyncClient) -> None:
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": "bank@example.com", "password": "supersecret1"},
    )
    parent_h = await _auth_headers(r.json()["access_token"])

    # insights blocked before connecting (consent-gated)
    r = await client.get("/api/v1/banking/insights", headers=parent_h)
    assert r.status_code == 409

    # status shows disconnected + a bank picker
    r = await client.get("/api/v1/banking/status", headers=parent_h)
    assert r.status_code == 200 and r.json()["connected"] is False
    assert len(r.json()["supported_banks"]) > 0

    # connect (simulated consent — no credentials)
    r = await client.post(
        "/api/v1/banking/connect", headers=parent_h, json={"bank_name": "مصرف المحاكاة"}
    )
    assert r.status_code == 200 and r.json()["connected"] is True

    # insights now available: categories + educational recommendations
    r = await client.get("/api/v1/banking/insights", headers=parent_h)
    assert r.status_code == 200, r.text
    ins = r.json()
    assert ins["simulated"] is True
    assert len(ins["categories"]) == 4
    assert sum(c["pct"] for c in ins["categories"]) >= 95  # ~100%
    assert len(ins["recommendations"]) >= 2

    # saving goal
    r = await client.post(
        "/api/v1/banking/goals",
        headers=parent_h,
        json={"title": "مكافأة 500 Robux", "target_amount": "500.00"},
    )
    assert r.status_code == 201, r.text
    goal = r.json()
    assert goal["remaining_amount"] == "500.00"
    assert goal["progress_pct"] == 0

    # disconnect
    r = await client.post("/api/v1/banking/disconnect", headers=parent_h)
    assert r.status_code == 200
    r = await client.get("/api/v1/banking/insights", headers=parent_h)
    assert r.status_code == 409  # consent revoked


@pytest.mark.asyncio
async def test_wrong_pin_and_refresh_rotation(client: AsyncClient) -> None:
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": "p2@example.com", "password": "supersecret1"},
    )
    assert r.status_code == 201
    tokens = r.json()
    parent_h = await _auth_headers(tokens["access_token"])

    r = await client.post(
        "/api/v1/children", headers=parent_h, json={"nickname": "Lina", "age_group": "5-7"}
    )
    child_id = r.json()["id"]
    await client.put(f"/api/v1/children/{child_id}/pin", headers=parent_h, json={"pin": "4321"})

    # wrong PIN rejected
    r = await client.post(
        "/api/v1/auth/child-login",
        headers=parent_h,
        json={"child_id": child_id, "pin": "0000"},
    )
    assert r.status_code == 401

    # refresh rotates: old refresh token becomes invalid
    r = await client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert r.status_code == 200, r.text
    r2 = await client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert r2.status_code == 401  # reused (rotated-out) token rejected
