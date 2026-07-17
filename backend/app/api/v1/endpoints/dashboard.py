from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_parent, get_db
from app.models.user import User
from app.schemas.child import ChildOut
from app.schemas.dashboard import ChildInsights, TimelinePoint
from app.schemas.game import SkillScores, SuccessPredictionOut
from app.schemas.reward import RewardOut
from app.services.insights_service import InsightsError, InsightsService

router = APIRouter()


@router.get("/children/{child_id}", response_model=ChildInsights)
async def child_insights(
    child_id: uuid.UUID,
    parent: User = Depends(get_current_parent),
    db: AsyncSession = Depends(get_db),
) -> ChildInsights:
    try:
        data = await InsightsService(db).child_overview(parent.id, child_id)
    except InsightsError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return ChildInsights(
        child=ChildOut.model_validate(data["child"]),
        skills=SkillScores(**data["skills"]),
        total_decisions=data["total_decisions"],
        resist_rate=data["resist_rate"],
        success_prediction=SuccessPredictionOut(**data["success_prediction"]),
        defeated_monsters=data["defeated_monsters"],
        rewards=[RewardOut.model_validate(r) for r in data["rewards"]],
    )


@router.get("/children/{child_id}/timeline", response_model=list[TimelinePoint])
async def child_timeline(
    child_id: uuid.UUID,
    parent: User = Depends(get_current_parent),
    db: AsyncSession = Depends(get_db),
) -> list[TimelinePoint]:
    try:
        points = await InsightsService(db).child_timeline(parent.id, child_id)
    except InsightsError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return [TimelinePoint(**p) for p in points]
