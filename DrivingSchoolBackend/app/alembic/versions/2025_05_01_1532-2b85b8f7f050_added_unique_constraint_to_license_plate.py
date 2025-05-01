"""Added unique constraint to license plate

Revision ID: 2b85b8f7f050
Revises: 206563c241a5
Create Date: 2025-05-01 15:32:59.077494

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2b85b8f7f050"
down_revision: Union[str, None] = "206563c241a5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(
        op.f("uq_vehicle_license_plate"), "vehicle", ["license_plate"]
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        op.f("uq_vehicle_license_plate"), "vehicle", type_="unique"
    )
