"""created user roles

Revision ID: 273e25c1f652
Revises: e2a86ccfbbe7
Create Date: 2025-04-30 01:13:04.393225

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "273e25c1f652"
down_revision: Union[str, None] = "e2a86ccfbbe7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Create roles ---
    op.execute("CREATE ROLE student_role;")
    op.execute("CREATE ROLE instructor_role;")
    op.execute("CREATE ROLE admin_role;")

    # --- Grant admin full access ---
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO admin_role;")
    op.execute("GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO admin_role;")

    # --- Student permissions ---
    op.execute("GRANT SELECT ON ALL TABLES IN SCHEMA public TO student_role;")
    op.execute("""GRANT UPDATE ON "user" TO student_role;""")

    # --- Instructor permissions ---
    op.execute("GRANT SELECT ON ALL TABLES IN SCHEMA public  TO instructor_role;")
    op.execute("""GRANT UPDATE ON "user" TO instructor_role;""")


def downgrade() -> None:
    # --- Revoke all privileges for roles before dropping them ---
    op.execute("REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM student_role;")
    op.execute("REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public FROM student_role;")
    op.execute("REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM instructor_role;")
    op.execute("REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public FROM instructor_role;")
    op.execute("REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM admin_role;")
    op.execute("REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public FROM admin_role;")

    # --- Drop roles ---
    op.execute("DROP ROLE IF EXISTS student_role;")
    op.execute("DROP ROLE IF EXISTS instructor_role;")
    op.execute("DROP ROLE IF EXISTS admin_role;")
