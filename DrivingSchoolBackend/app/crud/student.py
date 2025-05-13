from datetime import date
from typing import Literal

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, asc, desc, or_, exists
from sqlalchemy.orm import selectinload, joinedload

from core.models import User, Student, PracticeSchedule
from auth.utils import hash_password
from core.schemas.profile import StudentProfileSchema
from core.schemas.student import StudentCreateSchema, StudentUpdateSchema, StudentPaginatedReadSchema
from core.schemas.user import UserSchema
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

    category_level = await get_category_level_by_id(session, data.category_level_id)

    today = date.today()
    birthday = data.user.birthday
    age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))

    min_age = category_level.category_level_info.minimum_age_to_get
    if age < min_age:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Student must be at least {min_age} years old to enroll in this category level"
        )

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

    if data.password:
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


async def get_student_profile(session: AsyncSession, student_id: int):
    result = await session.execute(
        select(Student)
        .options(
            joinedload(Student.user),
            joinedload(Student.category_level),
            joinedload(Student.group)
        )
        .where(Student.id == student_id)
    )
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    return StudentProfileSchema(
        last_name=student.user.last_name,
        first_name=student.user.first_name,
        patronymic=student.user.patronymic or '',
        username=student.user.username,
        phone_number=student.user.phone_number,
        birthday=student.user.birthday,
        group=student.group.name,
        category=student.category_level.category,
        transmission=student.category_level.transmission
    )


async def get_students_paginated(
    session: AsyncSession,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "last_name",
    sort_order: Literal["asc", "desc"] = "asc",
    category_level_id: int | None = None,
    search: str | None = None,
    only_without_sch: bool = False
):
    if category_level_id:
        existing = await get_category_level_by_id(session, category_level_id)

    sort_fields = {
        "last_name": Student.user.property.mapper.class_.last_name,
        "first_name": Student.user.property.mapper.class_.first_name,
        "username": Student.user.property.mapper.class_.username,
    }

    sort_column = sort_fields.get(sort_by)
    if sort_column is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Unsupported sort field: {sort_by}')

    order_clause = asc(sort_column) if sort_order == "asc" else desc(sort_column)

    stmt = (
        select(Student)
        .join(Student.user)
        .options(selectinload(Student.user))
        .order_by(order_clause)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    if category_level_id:
        stmt = stmt.where(
            Student.category_level_id == category_level_id
        )

    if search:
        stmt = stmt.filter(
            or_(
                User.username.ilike(f"%{search}%"),
                User.first_name.ilike(f"%{search}%"),
                User.last_name.ilike(f"%{search}%"),
                User.patronymic.ilike(f"%{search}%"),
            )
        )

    if only_without_sch:
        stmt = stmt.where(
            ~exists().where(PracticeSchedule.student_id == Student.id)
        )

    res = await session.execute(stmt)
    students = res.scalars().all()

    from crud.practice_schedule import get_all_practice_schedules_by_student_id

    result = []
    for student in students:
        existing = await get_all_practice_schedules_by_student_id(session, student.id)

        result.append(
            StudentPaginatedReadSchema(
                id=student.id,
                category_level_id=student.category_level_id,
                group_id=student.group_id,
                user=UserSchema(
                    username=student.user.username,
                    first_name=student.user.first_name,
                    last_name=student.user.last_name,
                    patronymic=student.user.patronymic,
                    birthday=student.user.birthday,
                    phone_number=student.user.phone_number,
                ),
                has_schedule=(True if existing else False)
            )
        )

    return result
