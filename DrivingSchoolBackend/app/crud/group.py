from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, exists

from core.models import Group, GroupSchedule
from core.schemas.group import GroupCreateSchema, GroupUpdateSchema, GroupPaginatedReadSchema
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


async def get_groups_paginated(
    session: AsyncSession,
    page: int = 1,
    page_size: int = 10,
    category_level_id: int | None = None,
    search: str | None = None,
    only_without_sch: bool = False
):
    if category_level_id:
        existing = await get_category_level_by_id(session, category_level_id)

    stmt = (
        select(Group)
        .order_by(Group.name)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    if category_level_id:
        stmt = stmt.where(
            Group.category_level_id == category_level_id
        )

    if search:
        stmt = stmt.filter(
            Group.name.ilike(f"%{search}%")
        )

    if only_without_sch:
        stmt = stmt.where(
            ~exists().where(GroupSchedule.group_id == Group.id)
        )

    res = await session.execute(stmt)

    groups = res.scalars().all()

    from crud.group_schedule import get_group_schedules_by_group_id

    result = []
    for group in groups:
        existing = await get_group_schedules_by_group_id(session, group.id)

        result.append(
            GroupPaginatedReadSchema(
                id=group.id,
                name=group.name,
                created_date=group.created_date,
                category_level_id=group.category_level_id,
                instructor_id=group.instructor_id,
                has_schedule=(True if existing else False)
            )
        )

    return result


async def get_groups_by_category_level_id(session: AsyncSession, category_level_id: int):
    exists = await get_category_level_by_id(session, category_level_id)

    result = await session.execute(
        select(Group)
        .where(Group.category_level_id == category_level_id)
    )
    return result.scalars().all()