"""
Celery tasks related to notifications.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.notification import Notification


def _store_notification(
    recipient_id: int,
    sender_id: int,
    notification_type: str,
    message: str,
    post_id: Optional[int] = None,
    comment_id: Optional[int] = None,
) -> None:
    db = SessionLocal()
    try:
        db_notification = Notification(
            recipient_id=recipient_id,
            sender_id=sender_id,
            notification_type=notification_type,
            message=message,
            post_id=post_id,
            comment_id=comment_id,
            is_read=False,
        )
        db.add(db_notification)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@celery_app.task(name="app.tasks.notifications.create_notification")
def create_notification_task(
    recipient_id: int,
    sender_id: int,
    notification_type: str,
    message: str,
    post_id: Optional[int] = None,
    comment_id: Optional[int] = None,
) -> None:
    """Background task that writes a notification to the database."""
    _store_notification(
        recipient_id=recipient_id,
        sender_id=sender_id,
        notification_type=notification_type,
        message=message,
        post_id=post_id,
        comment_id=comment_id,
    )


def create_notification(
    recipient_id: int,
    sender_id: int,
    notification_type: str,
    message: str,
    post_id: Optional[int] = None,
    comment_id: Optional[int] = None,
) -> None:
    """
    Helper used inside API routes.
    Tries to enqueue the Celery task; if the broker is unreachable,
    it will fall back to a synchronous write to avoid losing the notification.
    """
    try:
        create_notification_task.delay(
            recipient_id=recipient_id,
            sender_id=sender_id,
            notification_type=notification_type,
            message=message,
            post_id=post_id,
            comment_id=comment_id,
        )
    except Exception:
        _store_notification(
            recipient_id=recipient_id,
            sender_id=sender_id,
            notification_type=notification_type,
            message=message,
            post_id=post_id,
            comment_id=comment_id,
        )


@celery_app.task(name="app.tasks.notifications.cleanup_old_notifications")
def cleanup_old_notifications(days: int = 30) -> dict:
    """Delete notifications that are read and older than the specified amount of days."""
    db = SessionLocal()
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        deleted = (
            db.query(Notification)
            .filter(Notification.is_read.is_(True), Notification.timestamp < cutoff)
            .delete(synchronize_session=False)
        )
        db.commit()
        return {"status": "success", "deleted": deleted}
    except Exception as exc:  # pragma: no cover - logged by Celery
        db.rollback()
        raise  # Re-raise to let Celery handle retries
    finally:
        db.close()

