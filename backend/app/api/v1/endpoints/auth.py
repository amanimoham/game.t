from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_parent, get_db
from app.models.user import User
from app.schemas.auth import ChildLogin, ParentLogin, ParentRegister, RefreshRequest
from app.schemas.common import Message, TokenPair
from app.schemas.user import UserOut
from app.services.auth_service import AuthError, AuthService
from app.services.child_service import ChildError, ChildService

router = APIRouter()


@router.post("/register", response_model=TokenPair, status_code=status.HTTP_201_CREATED)
async def register(body: ParentRegister, db: AsyncSession = Depends(get_db)) -> TokenPair:
    service = AuthService(db)
    try:
        user = await service.register_parent(body.email, body.password)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return await service.issue_tokens(str(user.id), user.role.value)


@router.post("/login", response_model=TokenPair)
async def login(body: ParentLogin, db: AsyncSession = Depends(get_db)) -> TokenPair:
    service = AuthService(db)
    try:
        user = await service.authenticate_parent(body.email, body.password)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    return await service.issue_tokens(str(user.id), user.role.value)


@router.post("/refresh", response_model=TokenPair)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)) -> TokenPair:
    service = AuthService(db)
    try:
        return await service.rotate(body.refresh_token)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


@router.post("/logout", response_model=Message)
async def logout(body: RefreshRequest, db: AsyncSession = Depends(get_db)) -> Message:
    await AuthService(db).logout(body.refresh_token)
    return Message(detail="Logged out")


@router.post("/child-login", response_model=TokenPair)
async def child_login(
    body: ChildLogin,
    parent: User = Depends(get_current_parent),
    db: AsyncSession = Depends(get_db),
) -> TokenPair:
    """Parent-managed: an authenticated parent hands the session to their child."""
    try:
        child = await ChildService(db).authenticate_child(parent.id, body.child_id, body.pin)
    except ChildError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    return await AuthService(db).issue_tokens(str(child.id), "child")


@router.get("/me", response_model=UserOut)
async def me(parent: User = Depends(get_current_parent)) -> User:
    return parent
