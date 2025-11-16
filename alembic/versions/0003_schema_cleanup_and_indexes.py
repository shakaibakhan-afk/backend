"""Schema cleanup: add comment_id to notifications, parent_id to comments with index, media_type to stories

Revision ID: 0003_schema_cleanup_and_indexes
Revises: 0002_story_views
Create Date: 2025-11-16
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine import Connection

# revision identifiers, used by Alembic.
revision = '0003_schema_cleanup_and_indexes'
down_revision = '0002_story_views'
branch_labels = None
depends_on = None


def _column_exists(conn: Connection, table: str, column: str) -> bool:
    res = conn.execute(sa.text(f"PRAGMA table_info({table})"))
    return any(row[1] == column for row in res.fetchall())


def upgrade() -> None:
    conn = op.get_bind()

    # notifications.comment_id
    if not _column_exists(conn, "notifications", "comment_id"):
        op.execute(sa.text("ALTER TABLE notifications ADD COLUMN comment_id INTEGER"))

    # comments.parent_id + index
    if not _column_exists(conn, "comments", "parent_id"):
        op.execute(sa.text("ALTER TABLE comments ADD COLUMN parent_id INTEGER"))
    # Create index if not exists
    op.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_comments_parent_id ON comments(parent_id)"))

    # stories.media_type with default 'image' NOT NULL
    if not _column_exists(conn, "stories", "media_type"):
        op.execute(
            sa.text("ALTER TABLE stories ADD COLUMN media_type VARCHAR(10) DEFAULT 'image' NOT NULL")
        )
        # Ensure any null/empty gets image
        op.execute(
            sa.text("UPDATE stories SET media_type = 'image' WHERE media_type IS NULL OR media_type = ''")
        )


def downgrade() -> None:
    # SQLite does not support DROP COLUMN easily; leave as no-op to keep safety
    pass


