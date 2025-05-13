"""added instructor age trigger

Revision ID: 90e3af67e692
Revises: 91d2187d008e
Create Date: 2025-05-13 20:46:18.533606

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "90e3af67e692"
down_revision: Union[str, None] = "91d2187d008e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE OR REPLACE FUNCTION check_instructor_age()
        RETURNS trigger AS $$
        DECLARE
            instructor_birthday DATE;
            min_age INT;
        BEGIN
            SELECT u.birthday INTO instructor_birthday
            FROM "user" u
            JOIN instructor i ON u.id = i.id
            WHERE i.id = NEW.instructor_id;

            SELECT cli.minimum_age_to_get INTO min_age
            FROM category_level_info cli
            WHERE cli.category_level_id = NEW.category_level_id;

            IF EXTRACT(YEAR FROM age(current_date, instructor_birthday)) < min_age THEN
                RAISE EXCEPTION 'Instructor is not old enough for chosen category level (% years). Birthday: %', 
                min_age, instructor_birthday;
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """)

    op.execute("""
        CREATE TRIGGER trg_check_instructor_age
        BEFORE INSERT ON instructor_category_level
        FOR EACH ROW
        EXECUTE FUNCTION check_instructor_age();
        """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TRIGGER IF EXISTS trg_check_instructor_age ON instructor_category_level;")
    op.execute("DROP FUNCTION IF EXISTS check_instructor_age();")
