"""
Celery tasks related to stories (cleanup expired stories, delete media, etc.).
"""
import os
from datetime import datetime, timezone

from app.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.social import Story


@celery_app.task(name="app.tasks.stories.cleanup_expired_stories")
def cleanup_expired_stories() -> dict:
    """Delete expired stories and remove the associated media from disk."""
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        expired = db.query(Story).filter(Story.expires_at <= now).all()
        removed = 0

        for story in expired:
            file_path = os.path.join("uploads", "stories", story.image)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError:
                    pass
            db.delete(story)
            removed += 1

        db.commit()
        return {"status": "success", "removed": removed}
    except Exception as exc:  # pragma: no cover - logged by Celery
        db.rollback()
        raise  # Re-raise to let Celery handle retries
    finally:
        db.close()

