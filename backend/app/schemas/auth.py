from __future__ import annotations

import uuid

from pydantic import BaseModel, EmailStr, Field


class ParentRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class ParentLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str


class ChildLogin(BaseModel):
    child_id: uuid.UUID
    pin: str = Field(min_length=4, max_length=8)
