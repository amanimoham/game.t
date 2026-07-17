from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_child, get_db
from app.models.child import Child
from app.schemas.game import (
    DecisionResult,
    DecisionSubmit,
    LevelOut,
    ProgressOut,
    RewardProgressOut,
    SessionOut,
    SkillScores,
    SuccessPredictionOut,
)
from app.services.game_service import GameError, GameService

router = APIRouter()


@router.get("/levels", response_model=list[LevelOut])
async def list_levels(
    child: Child = Depends(get_current_child),
    db: AsyncSession = Depends(get_db),
) -> list[LevelOut]:
    return [LevelOut.model_validate(level) for level in await GameService(db).get_levels()]


@router.post("/sessions", response_model=SessionOut)
async def start_session(
    child: Child = Depends(get_current_child),
    db: AsyncSession = Depends(get_db),
) -> SessionOut:
    data = await GameService(db).start_session(child)
    return SessionOut(
        session_id=data["session_id"],
        encouragement=data["encouragement"],
        skills=SkillScores(**data["skills"]),
        suggested_monster=data["suggested_monster"],
        difficulty=data["difficulty"],
    )


@router.post("/sessions/{session_id}/decisions", response_model=DecisionResult)
async def submit_decision(
    session_id: uuid.UUID,
    body: DecisionSubmit,
    child: Child = Depends(get_current_child),
    db: AsyncSession = Depends(get_db),
) -> DecisionResult:
    try:
        data = await GameService(db).submit_decision(
            child, session_id, body.challenge_id, body.choice_key, body.reaction_time_ms
        )
    except GameError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    rp = data.get("reward_progress")
    return DecisionResult(
        correct=data["correct"],
        defeated=data["defeated"],
        score_change=data["score_change"],
        skills=SkillScores(**data["skills"]),
        encouragement=data["encouragement"],
        next_suggested_monster=data["next_suggested_monster"],
        difficulty=data["difficulty"],
        success_prediction=SuccessPredictionOut(**data["success_prediction"]),
        reward_progress=RewardProgressOut(**rp) if rp else None,
    )


@router.get("/progress", response_model=ProgressOut)
async def get_progress(
    child: Child = Depends(get_current_child),
    db: AsyncSession = Depends(get_db),
) -> ProgressOut:
    data = await GameService(db).get_progress(child)
    return ProgressOut(
        skills=SkillScores(**data["skills"]),
        total_decisions=data["total_decisions"],
        resist_rate=data["resist_rate"],
        success_prediction=SuccessPredictionOut(**data["success_prediction"]),
    )
