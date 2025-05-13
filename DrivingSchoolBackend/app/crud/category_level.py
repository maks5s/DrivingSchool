from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from core.models import CategoryLevel, CategoryLevelInfo
from core.schemas.category_level import CategoryLevelUpdateSchema, CategoryLevelCreateSchema


async def create_category_level(session: AsyncSession, data: CategoryLevelCreateSchema):
    result = await session.execute(
        select(CategoryLevel).where(
            and_(
                CategoryLevel.category == data.category,
                CategoryLevel.transmission == data.transmission
            )
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category level with this category and transmission already exists"
        )

    category_level = CategoryLevel(
        category=data.category,
        transmission=data.transmission,
        description=data.description,
    )
    session.add(category_level)
    await session.flush()

    info = CategoryLevelInfo(
        category_level_id=category_level.id,
        theory_lessons_count=data.theory_lessons_count,
        practice_lessons_count=data.practice_lessons_count,
        theory_lessons_duration=data.theory_lessons_duration,
        practice_lessons_duration=data.practice_lessons_duration,
        minimum_age_to_get=data.minimum_age_to_get,
    )
    session.add(info)
    await session.commit()

    result = await session.execute(
        select(CategoryLevel)
        .options(selectinload(CategoryLevel.category_level_info))
        .where(CategoryLevel.id == category_level.id)
    )
    category_level = result.scalar_one()

    return category_level


async def update_category_level(session: AsyncSession, category_level_id: int, data: CategoryLevelUpdateSchema):
    result = await session.execute(
        select(CategoryLevel)
        .options(selectinload(CategoryLevel.category_level_info))
        .where(CategoryLevel.id == category_level_id)
    )
    category_level = result.scalar_one_or_none()
    if not category_level:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category level not found"
        )

    if (category_level.category != data.category or category_level.transmission != data.transmission):
        existing = await session.execute(
            select(CategoryLevel).where(
                and_(
                    CategoryLevel.category == data.category,
                    CategoryLevel.transmission == data.transmission,
                    CategoryLevel.id != category_level_id
                )
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Another category level with this category and transmission already exists"
            )

    category_level.category = data.category
    category_level.transmission = data.transmission
    category_level.description = data.description

    info = category_level.category_level_info
    info.theory_lessons_count = data.theory_lessons_count
    info.practice_lessons_count = data.practice_lessons_count
    info.theory_lessons_duration = data.theory_lessons_duration
    info.practice_lessons_duration = data.practice_lessons_duration
    info.minimum_age_to_get = data.minimum_age_to_get

    await session.commit()
    await session.refresh(category_level)
    return category_level


async def get_all_category_levels(session: AsyncSession):
    result = await session.execute(
        select(CategoryLevel).options(selectinload(CategoryLevel.category_level_info))
        .order_by(CategoryLevel.category, CategoryLevel.transmission)
    )
    return result.scalars().all()


async def get_category_level_by_id(session: AsyncSession, category_level_id: int):
    result = await session.execute(
        select(CategoryLevel)
        .options(selectinload(CategoryLevel.category_level_info))
        .where(CategoryLevel.id == category_level_id)
    )
    category_level = result.scalar_one_or_none()
    if not category_level:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category level not found")
    return category_level
