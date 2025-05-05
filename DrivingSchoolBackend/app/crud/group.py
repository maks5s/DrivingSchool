from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from core.models import Group
from core.schemas.group import GroupCreateSchema, GroupUpdateSchema
from crud.category_level import get_category_level_by_id
from crud.instructor import get_instructor_by_id
from crud.instructor_category import get_instructor_categories


async def create_group(session: AsyncSession, data: GroupCreateSchema):
    existing = await get_instructor_by_id(session, data.instructor_id)

    existing = await get_category_level_by_id(session, data.category_level_id)

    instructor_categories = await get_instructor_categories(session, data.instructor_id)
    instructor_categories_ids = [ic.id for ic in instructor_categories]
    if data.category_level_id not in instructor_categories_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Instructor has no such category level"
        )

    result = await session.execute(select(Group).where(Group.name == data.name))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group with this name already exists"
        )

    group = Group(**data.model_dump())
    session.add(group)
    await session.commit()
    await session.refresh(group)
    return group


async def update_group(session: AsyncSession, group_id: int, data: GroupUpdateSchema):
    result = await session.execute(select(Group).where(Group.id == group_id))
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Group not found")

    existing = await get_instructor_by_id(session, data.instructor_id)

    existing = await get_category_level_by_id(session, data.category_level_id)

    if group.name != data.name:
        existing = await session.execute(
            select(Group).where(
                and_(
                    Group.name == data.name,
                    Group.id != group_id
                )
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Another group with this name already exists"
            )

    for field, value in data.model_dump().items():
        setattr(group, field, value)

    await session.commit()
    await session.refresh(group)
    return group


async def get_all_groups(session: AsyncSession):
    result = await session.execute(select(Group))
    return result.scalars().all()


async def get_group_by_id(session: AsyncSession, group_id: int):
    result = await session.execute(select(Group).where(Group.id == group_id))
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    return group
