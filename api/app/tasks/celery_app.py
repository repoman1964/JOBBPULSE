"""Celery worker for api/. Generation currently runs in-process when Redis is down."""

from celery import Celery

from app.core.config import get_settings

settings = get_settings()
broker = settings.celery_broker_url or settings.redis_url
backend = settings.celery_result_backend or settings.redis_url

celery_app = Celery("jobpulse", broker=broker, backend=backend)
celery_app.conf.update(task_ignore_result=True, timezone="UTC")
