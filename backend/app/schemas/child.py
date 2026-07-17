from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AgeGroup


class ChildCreate(BaseModel):
    nickname: str = Field(min_length=1, max_length=50)
    age_group: AgeGroup


class ChildPinSet(BaseModel):
    pin: str = Field(min_length=4, max_length=8, pattern=r"^\d+$")


class ChildOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nickname: str
    age_group: AgeGroup
    created_at: datetime
