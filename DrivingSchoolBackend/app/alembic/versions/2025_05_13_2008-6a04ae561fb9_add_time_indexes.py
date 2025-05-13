"""add time indexes

Revision ID: 6a04ae561fb9
Revises: ee128c92953c
Create Date: 2025-05-13 20:08:37.750075

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6a04ae561fb9"
down_revision: Union[str, None] = "ee128c92953c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        op.f("ix_group_schedule_end_time"),
        "group_schedule",
        ["end_time"],
        unique=False,
    )
    op.create_index(
        op.f("ix_group_schedule_start_time"),
        "group_schedule",
        ["start_time"],
        unique=False,
    )
    op.create_index(
        op.f("ix_practice_schedule_end_time"),
        "practice_schedule",
        ["end_time"],
        unique=False,
    )
    op.create_index(
        op.f("ix_practice_schedule_start_time"),
        "practice_schedule",
        ["start_time"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_practice_schedule_start_time"), table_name="practice_schedule"
    )
    op.drop_index(
        op.f("ix_practice_schedule_end_time"), table_name="practice_schedule"
    )
    op.drop_index(
        op.f("ix_group_schedule_start_time"), table_name="group_schedule"
    )
    op.drop_index(
        op.f("ix_group_schedule_end_time"), table_name="group_schedule"
    )
