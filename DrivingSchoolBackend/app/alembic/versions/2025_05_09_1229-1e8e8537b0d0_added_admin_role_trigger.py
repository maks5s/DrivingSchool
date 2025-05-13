"""added admin_role trigger

Revision ID: 1e8e8537b0d0
Revises: 63ebf9e92186
Create Date: 2025-05-09 12:29:04.170808

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1e8e8537b0d0"
down_revision: Union[str, None] = "63ebf9e92186"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE OR REPLACE FUNCTION prevent_deleting_admin_user()
        RETURNS TRIGGER AS $$
        DECLARE
            is_admin BOOLEAN;
        BEGIN
            SELECT EXISTS (
                SELECT 1
                FROM pg_auth_members m
                JOIN pg_roles r_user ON r_user.oid = m.member
                JOIN pg_roles r_admin ON r_admin.oid = m.roleid
                WHERE r_user.rolname = OLD.username
                  AND r_admin.rolname = 'admin_role'
            ) INTO is_admin;

            IF is_admin THEN
                RAISE EXCEPTION 'Cannot delete a user with admin_role';
            END IF;

            RETURN OLD;
        END;
        $$ LANGUAGE plpgsql;
        """)

    op.execute("""
        CREATE TRIGGER trg_prevent_deleting_admin_user
        BEFORE DELETE ON "user"
        FOR EACH ROW
        EXECUTE FUNCTION prevent_deleting_admin_user();
        """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute('DROP TRIGGER IF EXISTS trg_prevent_deleting_admin_user ON "user";')
    op.execute('DROP FUNCTION IF EXISTS prevent_deleting_admin_user();')
