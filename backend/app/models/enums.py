"""Enumerations used across the domain.

Stored in Postgres as native ENUM types (see the initial migration). Members
carry explicit string *values*; models map them with ``values_callable`` so the
stored value is the clean lowercase string, not the member name.
"""
from __future__ import annotations

import enum


class UserRole(str, enum.Enum):
    PARENT = "parent"
    ADMIN = "admin"


class AgeGroup(str, enum.Enum):
    G_5_7 = "5-7"
    G_8_10 = "8-10"
    G_11_13 = "11-13"


class ConsentType(str, enum.Enum):
    DATA_COLLECTION = "data_collection"
    GAMEPLAY = "gameplay"


class RewardType(str, enum.Enum):
    ROBUX = "robux"


class RewardStatus(str, enum.Enum):
    LOCKED = "locked"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class SessionStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class MonsterCode(str, enum.Enum):
    INSTANT_REWARD = "instant_reward"
    SOCIAL_PRESSURE = "social_pressure"
    SPENDING = "spending"
    LIMITED_OFFER = "limited_offer"


class ActorType(str, enum.Enum):
    PARENT = "parent"
    CHILD = "child"
    ADMIN = "admin"
    SYSTEM = "system"


class ConnectionStatus(str, enum.Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"


class GoalStatus(str, enum.Enum):
    ACTIVE = "active"
    ACHIEVED = "achieved"
    CANCELLED = "cancelled"
