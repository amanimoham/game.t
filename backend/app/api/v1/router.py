"""Aggregate v1 API router."""
from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    banking,
    children,
    dashboard,
    game,
    health,
    rewards,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(children.router, prefix="/children", tags=["children"])
api_router.include_router(rewards.router, prefix="/rewards", tags=["rewards"])
api_router.include_router(game.router, prefix="/game", tags=["game"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(banking.router, prefix="/banking", tags=["banking"])
