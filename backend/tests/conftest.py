from __future__ import annotations

import asyncio
import sys

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# asyncpg requires the selector event loop on Windows.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.main import app


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
