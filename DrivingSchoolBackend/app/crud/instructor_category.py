from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import select, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import InstructorCategoryLevel, CategoryLevel
from crud.category_level import get_category_level_by_id
from crud.instructor import get_instructor_by_id


async def add_category_to_instructor(session: AsyncSession, instructor_id: int, category_level_id: int):
    instructor = await get_instructor_by_id(session, instructor_id)

    category_level = await get_category_level_by_id(session, category_level_id)

    today = date.today()
    birthday = instructor.user.birthday
    age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))

    min_age = category_level.category_level_info.minimum_age_to_get
    if age < min_age:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Instructor must be at least {min_age} years old to enroll in this category level"
        )

    exists = await session.execute(
        select(InstructorCategoryLevel).where(
            and_(
                InstructorCategoryLevel.instructor_id == instructor_id,
                InstructorCategoryLevel.category_level_id == category_level_id
            )
        )
    )
    if exists.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category already assigned to instructor"
        )

    link = InstructorCategoryLevel(
        instructor_id=instructor_id,
        category_level_id=category_level_id
    )
    session.add(link)
    await session.commit()
    return {"detail": "Category added to instructor"}


async def remove_category_from_instructor(session: AsyncSession, instructor_id: int, category_level_id: int):
    exists = await get_category_level_by_id(session, category_level_id)

    exists = await get_instructor_by_id(session, instructor_id)

    stmt = delete(InstructorCategoryLevel).where(
        and_(
            InstructorCategoryLevel.instructor_id == instructor_id,
            InstructorCategoryLevel.category_level_id == category_level_id
        )
    )
    result = await session.execute(stmt)
    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not assigned to instructor"
        )
    await session.commit()
    return {"detail": "Category removed from instructor"}


async def get_instructor_categories(session: AsyncSession, instructor_id: int):
    exists = await get_instructor_by_id(session, instructor_id)

    result = await session.execute(
        select(CategoryLevel)
        .join(InstructorCategoryLevel)
        .where(InstructorCategoryLevel.instructor_id == instructor_id)
    )
    return result.scalars().all()
