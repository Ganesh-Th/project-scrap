from celery import Celery
from app.config import settings

celery_app = Celery(
    "review_intelligence",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks.review_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
