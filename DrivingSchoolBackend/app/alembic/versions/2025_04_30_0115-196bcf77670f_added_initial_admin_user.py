"""added initial admin user

Revision ID: 196bcf77670f
Revises: 273e25c1f652
Create Date: 2025-04-30 01:15:10.850986

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from auth.utils import hash_password

# revision identifiers, used by Alembic.
revision: str = "196bcf77670f"
down_revision: Union[str, None] = "273e25c1f652"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Insert new user record in the 'user' table ---
    hashed_password = hash_password('admin')
    op.execute(f"""
        INSERT INTO "user" (username, hashed_password, first_name, last_name, birthday, phone_number)
        VALUES ('admin', '{hashed_password}', 'admin', 'admin', '01-01-1990', '+380680000000');
    """)

    # --- Create SQL user ---
    op.execute("""
        CREATE USER admin WITH PASSWORD 'admin';
    """)

    # --- Grant 'admin_role' role to the new user ---
    op.execute("""
        GRANT admin_role TO admin;
    """)


def downgrade() -> None:
    # --- Drop the user ---
    op.execute("""
        DROP USER IF EXISTS admin;
    """)

    # --- Remove the user record from the 'user' table ---
    op.execute("""
        DELETE FROM "user" WHERE username = 'admin';
    """)
