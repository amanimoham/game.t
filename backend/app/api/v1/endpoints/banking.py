from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_parent, get_db
from app.models.user import User
from app.schemas.banking import (
    BankConnectRequest,
    ConnectionStatusOut,
    GoalCreate,
    GoalOut,
    InsightsOut,
)
from app.schemas.common import Message
from app.services.banking_service import SUPPORTED_BANKS, BankingConnectionService
from app.services.goal_service import GoalError, GoalTrackingService
from app.services.transaction_analysis_service import (
    NotConnectedError,
    TransactionAnalysisService,
)

router = APIRouter()


def _status_payload(conn) -> ConnectionStatusOut:
    if conn is None:
        return ConnectionStatusOut(connected=False, status="disconnected", supported_banks=SUPPORTED_BANKS)
    return ConnectionStatusOut(
        connected=conn.status.value == "connected" and conn.consent_granted,
        status=conn.status.value,
        bank_name=conn.bank_name,
        last_synced_at=conn.last_synced_at,
        supported_banks=SUPPORTED_BANKS,
    )


@router.get("/status", response_model=ConnectionStatusOut)
async def status_(parent: User = Depends(get_current_parent), db: AsyncSession = Depends(get_db)) -> ConnectionStatusOut:
    conn = await BankingConnectionService(db).get(parent.id)
    return _status_payload(conn)


@router.post("/connect", response_model=ConnectionStatusOut)
async def connect(body: BankConnectRequest, parent: User = Depends(get_current_parent), db: AsyncSession = Depends(get_db)) -> ConnectionStatusOut:
    conn = await BankingConnectionService(db).connect(parent.id, body.bank_name)
    return _status_payload(conn)


@router.post("/disconnect", response_model=Message)
async def disconnect(parent: User = Depends(get_current_parent), db: AsyncSession = Depends(get_db)) -> Message:
    await BankingConnectionService(db).disconnect(parent.id)
    return Message(detail="تم إلغاء الربط")


@router.get("/insights", response_model=InsightsOut)
async def insights(parent: User = Depends(get_current_parent), db: AsyncSession = Depends(get_db)) -> InsightsOut:
    try:
        data = await TransactionAnalysisService(db).analyze(parent.id)
    except NotConnectedError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return InsightsOut(**data)


@router.get("/goals", response_model=list[GoalOut])
async def list_goals(parent: User = Depends(get_current_parent), db: AsyncSession = Depends(get_db)) -> list[GoalOut]:
    goals = await GoalTrackingService(db).list_goals(parent.id)
    return [GoalOut(**g) for g in goals]


@router.post("/goals", response_model=GoalOut, status_code=status.HTTP_201_CREATED)
async def create_goal(body: GoalCreate, parent: User = Depends(get_current_parent), db: AsyncSession = Depends(get_db)) -> GoalOut:
    try:
        await GoalTrackingService(db).create_goal(
            parent.id, body.title, body.target_amount, body.child_id, body.target_date
        )
    except GoalError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    goals = await GoalTrackingService(db).list_goals(parent.id)
    return GoalOut(**goals[0])
