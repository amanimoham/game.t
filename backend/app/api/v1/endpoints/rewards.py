from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_parent, get_db
from app.models.user import User
from app.schemas.reward import RewardCreate, RewardOut
from app.services.reward_order_service import RewardOrderError, RewardOrderService

router = APIRouter()


@router.post("", response_model=RewardOut, status_code=status.HTTP_201_CREATED)
async def create_reward(
    body: RewardCreate,
    parent: User = Depends(get_current_parent),
    db: AsyncSession = Depends(get_db),
) -> RewardOut:
    try:
        order = await RewardOrderService(db).create_order(
            parent.id, body.child_id, body.amount, body.reward_type
        )
    except RewardOrderError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return RewardOut.model_validate(order)


@router.get("/{reward_id}", response_model=RewardOut)
async def get_reward(
    reward_id: uuid.UUID,
    parent: User = Depends(get_current_parent),
    db: AsyncSession = Depends(get_db),
) -> RewardOut:
    order = await RewardOrderService(db).get_order(reward_id)
    if order is None or order.parent_id != parent.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reward not found")
    return RewardOut.model_validate(order)
