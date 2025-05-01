from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from sqlalchemy.orm import selectinload

from core.models import User, Instructor
from core.schemas.instructor import InstructorCreateSchema, InstructorUpdateSchema
from auth.utils import hash_password
from crud.user import get_user_by_username, get_user_by_phone_number


async def create_instructor(session: AsyncSession, data: InstructorCreateSchema):
    existing = await get_user_by_username(session, data.user.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username already exists"
        )

    existing = await get_user_by_phone_number(session, data.user.phone_number)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this phone number already exists"
        )

    user = User(
        username=data.user.username,
        first_name=data.user.first_name,
        last_name=data.user.last_name,
        patronymic=data.user.patronymic,
        birthday=data.user.birthday,
        phone_number=data.user.phone_number,
        hashed_password=hash_password(data.password),
    )
    session.add(user)
    await session.flush()

    instructor = Instructor(
        id=user.id,
        work_started_date=data.work_started_date,
    )
    session.add(instructor)

    create_query = text(f"""
        CREATE USER "{data.user.username}" WITH PASSWORD '{data.password}';
    """)
    grant_query = text(f"""
        GRANT instructor_role TO "{data.user.username}";
    """)
    await session.execute(create_query)
    await session.execute(grant_query)

    await session.commit()

    await session.refresh(instructor)

    result = await session.execute(
        select(Instructor)
        .options(selectinload(Instructor.user))
        .where(Instructor.id == instructor.id)
    )
    instructor = result.scalar_one()

    return instructor


async def update_instructor(session: AsyncSession, instructor_id: int, data: InstructorUpdateSchema):
    result = await session.execute(
        select(Instructor)
        .options(selectinload(Instructor.user))
        .where(Instructor.id == instructor_id)
    )
    instructor = result.scalar_one_or_none()
    if not instructor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Instructor not found"
        )

    # if instructor.user.username != data.user.username:
    #     existing = await get_user_by_username(session, data.user.username)
    #     if existing:
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail="Another user with this username already exists"
    #         )

    if instructor.user.username != data.user.username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot change username")

    if instructor.user.phone_number != data.user.phone_number:
        existing = await get_user_by_phone_number(session, data.user.phone_number)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Another user with this phone number already exists"
            )

    instructor.work_started_date = data.work_started_date

    user = instructor.user
    user.first_name = data.user.first_name
    user.last_name = data.user.last_name
    user.patronymic = data.user.patronymic
    user.birthday = data.user.birthday
    user.phone_number = data.user.phone_number

    new_hashed_password = hash_password(data.password)

    if user.hashed_password != new_hashed_password:
        user.hashed_password = new_hashed_password

        query = text(f"""
            ALTER USER "{user.username}" WITH PASSWORD '{data.password}';
        """)
        await session.execute(query)

    await session.commit()
    await session.refresh(instructor)
    return instructor


async def get_all_instructors(session: AsyncSession):
    result = await session.execute(
        select(Instructor).options(selectinload(Instructor.user))
    )
    return result.scalars().all()


async def get_instructor_by_id(session: AsyncSession, instructor_id: int):
    result = await session.execute(
        select(Instructor)
        .options(selectinload(Instructor.user))
        .where(Instructor.id == instructor_id)
    )
    instructor = result.scalar_one_or_none()
    if not instructor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instructor not found")
    return instructor
