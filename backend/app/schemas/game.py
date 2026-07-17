from __future__ import annotations

import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ChallengeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    scenario: str
    choices: list
    points: int
    is_final: bool
    order_index: int
    monster_code: str | None = None


class LevelOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    difficulty: int
    required_score: int
    order_index: int
    challenges: list[ChallengeOut] = []


class SkillScores(BaseModel):
    patience: float
    saving_awareness: float
    impulse_control: float


class SuccessPredictionOut(BaseModel):
    probability: float
    label: str


class SessionOut(BaseModel):
    session_id: uuid.UUID
    encouragement: str
    skills: SkillScores
    suggested_monster: str
    difficulty: int


class DecisionSubmit(BaseModel):
    challenge_id: uuid.UUID
    choice_key: str = Field(min_length=1, max_length=10)
    reaction_time_ms: int | None = Field(default=None, ge=0)


class RewardProgressOut(BaseModel):
    reward_id: uuid.UUID | None = None
    progress_pct: int
    unlocked_amount: Decimal
    amount: Decimal | None = None
    status: str | None = None


class DecisionResult(BaseModel):
    correct: bool
    defeated: bool
    score_change: int
    skills: SkillScores
    encouragement: str
    next_suggested_monster: str
    difficulty: int
    success_prediction: SuccessPredictionOut
    reward_progress: RewardProgressOut | None = None


class ProgressOut(BaseModel):
    skills: SkillScores
    total_decisions: int
    resist_rate: float
    success_prediction: SuccessPredictionOut
