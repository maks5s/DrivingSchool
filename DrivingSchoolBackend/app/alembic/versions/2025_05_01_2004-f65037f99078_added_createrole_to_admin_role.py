"""added createrole to admin_role

Revision ID: f65037f99078
Revises: 129816a8673f
Create Date: 2025-05-01 20:04:26.085549

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f65037f99078"
down_revision: Union[str, None] = "129816a8673f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER ROLE admin_role CREATEROLE;")
    op.execute("ALTER USER admin CREATEROLE;")
    op.execute("GRANT instructor_role TO admin WITH ADMIN OPTION;")
    op.execute("GRANT student_role TO admin WITH ADMIN OPTION;")


def downgrade() -> None:
    """Downgrade schema."""
    pass
