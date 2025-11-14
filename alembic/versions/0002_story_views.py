"""add story views table

Revision ID: 0002_story_views
Revises: 0001_prepare_base
Create Date: 2025-11-14 11:30:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0002_story_views"
down_revision = "0001_prepare_base"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "story_views",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("story_id", sa.Integer(), nullable=False),
        sa.Column("viewer_id", sa.Integer(), nullable=False),
        sa.Column("viewed_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.ForeignKeyConstraint(["story_id"], ["stories.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["viewer_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("story_id", "viewer_id", name="unique_story_view"),
    )
    op.create_index("ix_story_views_story_id", "story_views", ["story_id"], unique=False)
    op.create_index("ix_story_views_viewer_id", "story_views", ["viewer_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_story_views_viewer_id", table_name="story_views")
    op.drop_index("ix_story_views_story_id", table_name="story_views")
    op.drop_table("story_views")

