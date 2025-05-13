"""add time constraints

Revision ID: 0e47cbc0fec7
Revises: 90e3af67e692
Create Date: 2025-05-13 21:00:33.917894

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0e47cbc0fec7"
down_revision: Union[str, None] = "90e3af67e692"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_check_constraint(
        constraint_name="ck_group_schedule_start_end_time",
        table_name="group_schedule",
        condition="end_time > start_time"
    )
    op.create_check_constraint(
        constraint_name="ck_practice_schedule_start_end_time",
        table_name="practice_schedule",
        condition="end_time > start_time"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        constraint_name="ck_practice_schedule_start_end_time",
        table_name="practice_schedule",
        type_="check"
    )
    op.drop_constraint(
        constraint_name="ck_group_schedule_start_end_time",
        table_name="group_schedule",
        type_="check"
    )
