"""Added unique constraints

Revision ID: 206563c241a5
Revises: 196bcf77670f
Create Date: 2025-05-01 01:26:14.027568

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "206563c241a5"
down_revision: Union[str, None] = "196bcf77670f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(
        op.f("uq_category_level_category_transmission"),
        "category_level",
        ["category", "transmission"],
    )
    op.create_unique_constraint(
        op.f("uq_category_level_info_category_level_id"),
        "category_level_info",
        ["category_level_id"],
    )
    op.create_unique_constraint(op.f("uq_instructor_id"), "instructor", ["id"])
    op.create_unique_constraint(
        op.f("uq_instructor_category_level_instructor_id_category_level_id"),
        "instructor_category_level",
        ["instructor_id", "category_level_id"],
    )
    op.create_unique_constraint(op.f("uq_student_id"), "student", ["id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(op.f("uq_student_id"), "student", type_="unique")
    op.drop_constraint(
        op.f("uq_instructor_category_level_instructor_id_category_level_id"),
        "instructor_category_level",
        type_="unique",
    )
    op.drop_constraint(op.f("uq_instructor_id"), "instructor", type_="unique")
    op.drop_constraint(
        op.f("uq_category_level_info_category_level_id"),
        "category_level_info",
        type_="unique",
    )
    op.drop_constraint(
        op.f("uq_category_level_category_transmission"),
        "category_level",
        type_="unique",
    )
