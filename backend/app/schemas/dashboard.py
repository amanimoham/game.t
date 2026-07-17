from __future__ import annotations

import uuid

from pydantic import BaseModel

from app.schemas.child import ChildOut
from app.schemas.game import SkillScores, SuccessPredictionOut
from app.schemas.reward import RewardOut


class ChildInsights(BaseModel):
    child: ChildOut
    skills: SkillScores
    total_decisions: int
    resist_rate: float
    success_prediction: SuccessPredictionOut
    defeated_monsters: list[str]
    rewards: list[RewardOut]
