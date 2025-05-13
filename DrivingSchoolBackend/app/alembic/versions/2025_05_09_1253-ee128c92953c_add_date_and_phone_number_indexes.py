"""add date and phone_number indexes

Revision ID: ee128c92953c
Revises: 1e8e8537b0d0
Create Date: 2025-05-09 12:53:40.034444

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ee128c92953c"
down_revision: Union[str, None] = "1e8e8537b0d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        op.f("ix_group_schedule_date"),
        "group_schedule",
        ["date"],
        unique=False,
    )
    op.create_index(
        op.f("ix_practice_schedule_date"),
        "practice_schedule",
        ["date"],
        unique=False,
    )
    op.drop_constraint("uq_user_phone_number", "user", type_="unique")
    op.create_index(
        op.f("ix_user_phone_number"), "user", ["phone_number"], unique=True
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_user_phone_number"), table_name="user")
    op.create_unique_constraint(
        "uq_user_phone_number", "user", ["phone_number"]
    )
    op.drop_index(
        op.f("ix_practice_schedule_date"), table_name="practice_schedule"
    )
    op.drop_index(op.f("ix_group_schedule_date"), table_name="group_schedule")
