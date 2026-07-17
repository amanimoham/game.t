from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_parent, get_db
from app.models.user import User
from app.schemas.child import ChildCreate, ChildOut, ChildPinSet
from app.schemas.common import Message
from app.services.child_service import ChildError, ChildService

router = APIRouter()


@router.post("", response_model=ChildOut, status_code=status.HTTP_201_CREATED)
async def create_child(
    body: ChildCreate,
    parent: User = Depends(get_current_parent),
    db: AsyncSession = Depends(get_db),
) -> ChildOut:
    child = await ChildService(db).create_child(parent.id, body.nickname, body.age_group)
    return ChildOut.model_validate(child)


@router.get("", response_model=list[ChildOut])
async def list_children(
    parent: User = Depends(get_current_parent),
    db: AsyncSession = Depends(get_db),
) -> list[ChildOut]:
    children = await ChildService(db).list_children(parent.id)
    return [ChildOut.model_validate(c) for c in children]


@router.put("/{child_id}/pin", response_model=Message)
async def set_pin(
    child_id: uuid.UUID,
    body: ChildPinSet,
    parent: User = Depends(get_current_parent),
    db: AsyncSession = Depends(get_db),
) -> Message:
    try:
        await ChildService(db).set_pin(parent.id, child_id, body.pin)
    except ChildError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Message(detail="PIN updated")
