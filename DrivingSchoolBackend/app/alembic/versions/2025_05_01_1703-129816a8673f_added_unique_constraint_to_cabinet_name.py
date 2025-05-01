"""Added unique constraint to cabinet name

Revision ID: 129816a8673f
Revises: 2b85b8f7f050
Create Date: 2025-05-01 17:03:18.683963

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "129816a8673f"
down_revision: Union[str, None] = "2b85b8f7f050"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(op.f("uq_cabinet_name"), "cabinet", ["name"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(op.f("uq_cabinet_name"), "cabinet", type_="unique")
