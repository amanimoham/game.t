"""Celery application (Redis broker/backend).

Used from later steps for async analytics ingestion and AI feature building.
A message broker (RabbitMQ/Kafka) can replace Redis here without touching
call sites when scale demands it.
"""
from __future__ import annotations

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "savings_game",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)
