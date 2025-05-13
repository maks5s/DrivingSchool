"""added student age trigger

Revision ID: 91d2187d008e
Revises: 6a04ae561fb9
Create Date: 2025-05-13 20:43:00.740983

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "91d2187d008e"
down_revision: Union[str, None] = "6a04ae561fb9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE OR REPLACE FUNCTION check_student_age()
        RETURNS trigger AS $$
        DECLARE
            student_birthday date;
            min_age int;
        BEGIN
            SELECT birthday INTO student_birthday
            FROM "user"
            WHERE id = NEW.id;

            SELECT cli.minimum_age_to_get INTO min_age
            FROM category_level_info cli
            WHERE cli.category_level_id = NEW.category_level_id;

            IF EXTRACT(YEAR FROM age(current_date, student_birthday)) < min_age THEN
                RAISE EXCEPTION 'Student is not old enough for chosen category level. Minimal age: %, birthday: %', 
                min_age, student_birthday;
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """)

    op.execute("""
        CREATE TRIGGER trg_check_student_age
        BEFORE INSERT OR UPDATE ON student
        FOR EACH ROW
        EXECUTE FUNCTION check_student_age();
        """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TRIGGER IF EXISTS trg_check_student_age ON student;")
    op.execute("DROP FUNCTION IF EXISTS check_student_age();")
