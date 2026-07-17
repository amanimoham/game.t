"""Model registry.

Importing every model here ensures they are all attached to ``Base.metadata``
(so Alembic and relationship resolution see the full schema) simply by
importing ``app.models``.
"""
from app.models.analytics import BehaviorEvent, ChildDecision, ChildProfile
from app.models.audit import AuditLog
from app.models.banking import BankConnection, SavingGoal
from app.models.child import Child
from app.models.consent import ParentalConsent
from app.models.game import Challenge, GameSession, Level, MonsterType
from app.models.reward import RewardOrder, RewardUnlockEvent
from app.models.user import User

__all__ = [
    "User",
    "Child",
    "ParentalConsent",
    "RewardOrder",
    "RewardUnlockEvent",
    "Level",
    "MonsterType",
    "Challenge",
    "GameSession",
    "ChildDecision",
    "ChildProfile",
    "BehaviorEvent",
    "AuditLog",
    "BankConnection",
    "SavingGoal",
]
