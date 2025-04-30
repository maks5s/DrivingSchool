from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import User


async def get_user_by_username(
    session: AsyncSession,
    username: str,
):
    result = await session.execute(
        select(User).where(User.username == username)
    )
    return result.scalar_one_or_none()


async def get_user_by_id(
    session: AsyncSession,
    user_id: int,
):
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()


async def get_user_role_by_username(
    session: AsyncSession,
    username: str
):
    query = text("""
        SELECT r.rolname
        FROM pg_roles u
        JOIN pg_auth_members m ON u.oid = m.member
        JOIN pg_roles r ON m.roleid = r.oid
        WHERE u.rolname = :username;
    """)
    result = await session.execute(query, {"username": username})
    row = result.fetchone()
    return row[0] if row else None
