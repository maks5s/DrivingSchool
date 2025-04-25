"""Initial database migration

Revision ID: 0263488ad491
Revises:
Create Date: 2025-04-25 23:30:32.147925

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0263488ad491"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "cabinet",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=16), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_cabinet")),
    )
    op.create_table(
        "category_level",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(length=10), nullable=False),
        sa.Column("transmission", sa.String(length=32), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_category_level")),
    )
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("first_name", sa.String(length=50), nullable=False),
        sa.Column("last_name", sa.String(length=50), nullable=False),
        sa.Column("patronymic", sa.String(length=50), nullable=True),
        sa.Column("birthday", sa.Date(), nullable=False),
        sa.Column("phone_number", sa.String(length=15), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user")),
        sa.UniqueConstraint("phone_number", name=op.f("uq_user_phone_number")),
    )
    op.create_index(
        op.f("ix_user_username"), "user", ["username"], unique=True
    )
    op.create_table(
        "category_level_info",
        sa.Column("category_level_id", sa.Integer(), nullable=False),
        sa.Column("theory_lessons_count", sa.Integer(), nullable=False),
        sa.Column("practice_lessons_count", sa.Integer(), nullable=False),
        sa.Column("theory_lessons_duration", sa.Time(), nullable=False),
        sa.Column("practice_lessons_duration", sa.Time(), nullable=False),
        sa.Column("minimum_age_to_get", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["category_level_id"],
            ["category_level.id"],
            name=op.f(
                "fk_category_level_info_category_level_id_category_level"
            ),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "category_level_id", name=op.f("pk_category_level_info")
        ),
        sa.UniqueConstraint(
            "category_level_id",
            name=op.f("uq_category_level_info_category_level_id"),
        ),
    )
    op.create_table(
        "instructor",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("work_started_date", sa.Date(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            name=op.f("fk_instructor_user_id_user"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_instructor")),
        sa.UniqueConstraint("user_id", name=op.f("uq_instructor_user_id")),
    )
    op.create_table(
        "vehicle",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("brand", sa.String(length=50), nullable=False),
        sa.Column("model", sa.String(length=50), nullable=False),
        sa.Column("manufacture_year", sa.Integer(), nullable=False),
        sa.Column("license_plate", sa.String(length=20), nullable=False),
        sa.Column("fuel_type", sa.String(length=20), nullable=False),
        sa.Column("category_level_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["category_level_id"],
            ["category_level.id"],
            name=op.f("fk_vehicle_category_level_id_category_level"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_vehicle")),
    )
    op.create_table(
        "group",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("created_date", sa.Date(), nullable=False),
        sa.Column("category_level_id", sa.Integer(), nullable=False),
        sa.Column("instructor_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["category_level_id"],
            ["category_level.id"],
            name=op.f("fk_group_category_level_id_category_level"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["instructor_id"],
            ["instructor.id"],
            name=op.f("fk_group_instructor_id_instructor"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_group")),
    )
    op.create_table(
        "instructor_category_level",
        sa.Column("instructor_id", sa.Integer(), nullable=False),
        sa.Column("category_level_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["category_level_id"],
            ["category_level.id"],
            name=op.f(
                "fk_instructor_category_level_category_level_id_category_level"
            ),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["instructor_id"],
            ["instructor.id"],
            name=op.f("fk_instructor_category_level_instructor_id_instructor"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "instructor_id",
            "category_level_id",
            name=op.f("pk_instructor_category_level"),
        ),
        sa.UniqueConstraint(
            "instructor_id",
            "category_level_id",
            name=op.f(
                "uq_instructor_category_level_instructor_id_category_level_id"
            ),
        ),
    )
    op.create_table(
        "group_schedule",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("cabinet_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["cabinet_id"],
            ["cabinet.id"],
            name=op.f("fk_group_schedule_cabinet_id_cabinet"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["group.id"],
            name=op.f("fk_group_schedule_group_id_group"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_group_schedule")),
    )
    op.create_table(
        "student",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("category_level_id", sa.Integer(), nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["category_level_id"],
            ["category_level.id"],
            name=op.f("fk_student_category_level_id_category_level"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["group.id"],
            name=op.f("fk_student_group_id_group"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            name=op.f("fk_student_user_id_user"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_student")),
        sa.UniqueConstraint("user_id", name=op.f("uq_student_user_id")),
    )
    op.create_table(
        "practice_schedule",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("instructor_id", sa.Integer(), nullable=False),
        sa.Column("vehicle_id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["instructor_id"],
            ["instructor.id"],
            name=op.f("fk_practice_schedule_instructor_id_instructor"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["student.id"],
            name=op.f("fk_practice_schedule_student_id_student"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["vehicle_id"],
            ["vehicle.id"],
            name=op.f("fk_practice_schedule_vehicle_id_vehicle"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_practice_schedule")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("practice_schedule")
    op.drop_table("student")
    op.drop_table("group_schedule")
    op.drop_table("instructor_category_level")
    op.drop_table("group")
    op.drop_table("vehicle")
    op.drop_table("instructor")
    op.drop_table("category_level_info")
    op.drop_index(op.f("ix_user_username"), table_name="user")
    op.drop_table("user")
    op.drop_table("category_level")
    op.drop_table("cabinet")
