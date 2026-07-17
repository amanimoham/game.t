"""BankingConnectionService — manages a parent's (simulated) Open Banking link.

MVP: a consent-gated simulated connection. No credentials, account numbers, or
balances are ever collected or stored. Swap this service's internals for a real
Saudi Open Banking aggregator later without touching callers.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.models.banking import BankConnection
from app.models.enums import ActorType, ConnectionStatus

# Institutions offered in the simulated picker (no real integration).
SUPPORTED_BANKS = [
    "بنك التجربة الأول",
    "مصرف المحاكاة",
    "بنك الادخار التعليمي",
    "المصرف الرقمي التجريبي",
]


class BankingConnectionService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get(self, parent_id: uuid.UUID) -> BankConnection | None:
        result = await self.db.execute(
            select(BankConnection).where(BankConnection.parent_id == parent_id)
        )
        return result.scalar_one_or_none()

    async def connect(self, parent_id: uuid.UUID, bank_name: str) -> BankConnection:
        now = datetime.now(timezone.utc)
        conn = await self.get(parent_id)
        if conn is None:
            conn = BankConnection(parent_id=parent_id)
            self.db.add(conn)
        conn.bank_name = bank_name
        conn.status = ConnectionStatus.CONNECTED
        conn.consent_granted = True
        conn.connected_at = now
        conn.last_synced_at = now
        self.db.add(
            AuditLog(
                actor_type=ActorType.PARENT,
                actor_id=parent_id,
                action="banking.connected",
                entity_type="bank_connection",
                event_metadata={"bank": bank_name, "simulated": True},
            )
        )
        await self.db.commit()
        await self.db.refresh(conn)
        return conn

    async def disconnect(self, parent_id: uuid.UUID) -> None:
        conn = await self.get(parent_id)
        if conn is not None:
            conn.status = ConnectionStatus.DISCONNECTED
            conn.consent_granted = False
            self.db.add(
                AuditLog(
                    actor_type=ActorType.PARENT,
                    actor_id=parent_id,
                    action="banking.disconnected",
                    entity_type="bank_connection",
                )
            )
            await self.db.commit()

    async def is_connected(self, parent_id: uuid.UUID) -> bool:
        conn = await self.get(parent_id)
        return bool(conn and conn.status == ConnectionStatus.CONNECTED and conn.consent_granted)
