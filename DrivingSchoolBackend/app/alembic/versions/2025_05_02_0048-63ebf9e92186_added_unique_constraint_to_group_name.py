"""Added unique constraint to group name

Revision ID: 63ebf9e92186
Revises: f65037f99078
Create Date: 2025-05-02 00:48:59.607441

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "63ebf9e92186"
down_revision: Union[str, None] = "f65037f99078"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(op.f("uq_group_name"), "group", ["name"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(op.f("uq_group_name"), "group", type_="unique")
