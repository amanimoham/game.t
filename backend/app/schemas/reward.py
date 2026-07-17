from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import RewardStatus, RewardType


class RewardCreate(BaseModel):
    child_id: uuid.UUID
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    reward_type: RewardType = RewardType.ROBUX


class RewardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    child_id: uuid.UUID
    reward_type: RewardType
    amount: Decimal
    status: RewardStatus
    unlocked_amount: Decimal
    progress_pct: int
    created_at: datetime
    completed_at: datetime | None = None
    delivered_at: datetime | None = None
