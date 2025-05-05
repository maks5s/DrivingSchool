from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import User
from core.schemas.profile import AdminProfileSchema


async def get_admin_profile(session: AsyncSession, admin_id: int):
    result = await session.execute(select(User).where(User.id == admin_id))
    admin = result.scalar_one_or_none()
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")

    return AdminProfileSchema(
        last_name=admin.last_name,
        first_name=admin.first_name,
        patronymic=admin.patronymic or '',
        username=admin.username,
        phone_number=admin.phone_number,
        birthday=admin.birthday,
    )

