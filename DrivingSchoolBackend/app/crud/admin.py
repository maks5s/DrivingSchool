from fastapi import HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from auth.utils import hash_password
from core.models import User
from core.schemas.admin import AdminUpdateSchema
from core.schemas.profile import AdminProfileSchema
from crud.user import get_user_by_phone_number


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


async def update_admin(session: AsyncSession, admin_id: int, data: AdminUpdateSchema):
    result = await session.execute(
        select(User)
        .where(User.id == admin_id)
    )
    admin = result.scalar_one_or_none()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin not found"
        )

    if admin.username != data.user.username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot change username")

    if admin.phone_number != data.user.phone_number:
        existing = await get_user_by_phone_number(session, data.user.phone_number)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Another user with this phone number already exists"
            )

    user = admin
    user.first_name = data.user.first_name
    user.last_name = data.user.last_name
    user.patronymic = data.user.patronymic
    user.birthday = data.user.birthday
    user.phone_number = data.user.phone_number

    if data.password:
        new_hashed_password = hash_password(data.password)

        if user.hashed_password != new_hashed_password:
            user.hashed_password = new_hashed_password

            query = text(f"""
                ALTER USER "{user.username}" WITH PASSWORD '{data.password}';
            """)
            await session.execute(query)

    await session.commit()
    await session.refresh(admin)
    return admin
