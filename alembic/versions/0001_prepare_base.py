"""Initial empty revision.

This file is a placeholder so developers can immediately run
`alembic revision --autogenerate -m "describe change"` to capture
the current SQLAlchemy models as migrations.
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0001_prepare_base"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass


