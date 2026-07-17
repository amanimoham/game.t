from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class BankConnectRequest(BaseModel):
    bank_name: str = Field(min_length=2, max_length=120)


class ConnectionStatusOut(BaseModel):
    connected: bool
    status: str
    bank_name: str | None = None
    last_synced_at: datetime | None = None
    supported_banks: list[str] = []


class CategoryOut(BaseModel):
    key: str
    label: str
    amount: int
    pct: int


class InsightsOut(BaseModel):
    simulated: bool
    monthly_total: int
    categories: list[CategoryOut]
    recommendations: list[str]


class GoalCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    target_amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    child_id: uuid.UUID | None = None
    target_date: date | None = None


class GoalOut(BaseModel):
    id: uuid.UUID
    title: str
    target_amount: Decimal
    current_amount: Decimal
    remaining_amount: Decimal
    currency: str
    progress_pct: int
    days_remaining: int | None = None
    status: str
