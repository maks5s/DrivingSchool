from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from sqlalchemy.orm import selectinload

from core.models import User, Student
from auth.utils import hash_password
from core.schemas.student import StudentCreateSchema, StudentUpdateSchema
from crud.category_level import get_category_level_by_id
from crud.group import get_group_by_id
from crud.user import get_user_by_username, get_user_by_phone_number


async def create_student(session: AsyncSession, data: StudentCreateSchema):
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

    existing = await get_category_level_by_id(session, data.category_level_id)

    group = await get_group_by_id(session, data.group_id)
    if group.category_level_id != data.category_level_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group has no such category level"
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

    student = Student(
        id=user.id,
        category_level_id=data.category_level_id,
        group_id=data.group_id
    )
    session.add(student)

    create_query = text(f"""
        CREATE USER "{data.user.username}" WITH PASSWORD '{data.password}';
    """)
    grant_query = text(f"""
        GRANT student_role TO "{data.user.username}";
    """)
    await session.execute(create_query)
    await session.execute(grant_query)

    await session.commit()

    await session.refresh(student)

    result = await session.execute(
        select(Student)
        .options(selectinload(Student.user))
        .where(Student.id == student.id)
    )
    student = result.scalar_one()

    return student


async def update_student(session: AsyncSession, student_id: int, data: StudentUpdateSchema):
    result = await session.execute(
        select(Student)
        .options(selectinload(Student.user))
        .where(Student.id == student_id)
    )
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student not found"
        )

    existing = await get_category_level_by_id(session, data.category_level_id)

    group = await get_group_by_id(session, data.group_id)
    if group.category_level_id != data.category_level_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group has no such category level"
        )

    # if student.user.username != data.user.username:
    #     existing = await get_user_by_username(session, data.user.username)
    #     if existing:
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail="Another user with this username already exists"
    #         )

    if student.user.username != data.user.username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot change username")

    if student.user.phone_number != data.user.phone_number:
        existing = await get_user_by_phone_number(session, data.user.phone_number)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Another user with this phone number already exists"
            )

    student.category_level_id = data.category_level_id
    student.group_id = data.group_id

    user = student.user
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
    await session.refresh(student)
    return student


async def get_all_students(session: AsyncSession):
    result = await session.execute(
        select(Student).options(selectinload(Student.user))
    )
    return result.scalars().all()


async def get_student_by_id(session: AsyncSession, student_id: int):
    result = await session.execute(
        select(Student)
        .options(selectinload(Student.user))
        .where(Student.id == student_id)
    )
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return student
