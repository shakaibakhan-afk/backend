"""
Celery application configuration for background tasks.
"""
from celery import Celery
from celery.schedules import crontab

from app.core.config import settings


celery_app = Celery(
    "instagram_clone",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.notifications",
        "app.tasks.stories",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=500,
)

celery_app.conf.beat_schedule = {
    "cleanup-expired-stories": {
        "task": "app.tasks.stories.cleanup_expired_stories",
        "schedule": crontab(minute="*/10"),  # every 10 minutes
    },
    "cleanup-old-notifications": {
        "task": "app.tasks.notifications.cleanup_old_notifications",
        "schedule": crontab(hour=2, minute=0),  # daily at 02:00 UTC
        "kwargs": {"days": 30},
    },
}


if __name__ == "__main__":
    celery_app.start()


