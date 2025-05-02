from datetime import date, timedelta

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from core.models import GroupSchedule
from core.schemas.group_schedule import GroupScheduleCreateSchema, GroupScheduleUpdateSchema, GroupScheduleSchema
from crud.cabinet import get_cabinet_by_id
from crud.group import get_group_by_id


async def check_schedule_conflict(session: AsyncSession, data: GroupScheduleSchema, schedule_id: int | None = None):
    filters = [
        GroupSchedule.date == data.date,
        or_(
            and_(GroupSchedule.start_time <= data.start_time, GroupSchedule.end_time > data.start_time),
            and_(GroupSchedule.start_time < data.end_time, GroupSchedule.end_time >= data.end_time),
            and_(GroupSchedule.start_time >= data.start_time, GroupSchedule.end_time <= data.end_time),
        )
    ]
    if schedule_id:
        exclude_self = GroupSchedule.id != schedule_id
    else:
        exclude_self = True

    # Cabinet
    cabinet_query = select(GroupSchedule).where(
        and_(
            *filters,
            GroupSchedule.cabinet_id == data.cabinet_id,
            exclude_self
        )
    )

    # Group
    group_query = select(GroupSchedule).where(
        and_(
            *filters,
            GroupSchedule.group_id == data.group_id,
            exclude_self
        )
    )

    cabinet_result = await session.execute(cabinet_query)
    group_result = await session.execute(group_query)

    if cabinet_result.scalar_one_or_none():
        return "cabinet"
    if group_result.scalar_one_or_none():
        return "group"
    return None


async def create_group_schedule(session: AsyncSession, data: GroupScheduleCreateSchema):
    today = date.today()
    if data.date <= today:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Wrong date: date should be at least tomorrow ({today + timedelta(days=1)})"
        )

    if data.start_time >= data.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong time: end time should be greater than start time"
        )

    existing = await get_group_by_id(session, data.group_id)

    existing = await get_cabinet_by_id(session, data.cabinet_id)

    conflict_type = await check_schedule_conflict(session, data)
    if conflict_type == "cabinet":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Schedule conflict detected: this cabinet already has a lesson at that time"
        )
    elif conflict_type == "group":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Schedule conflict detected: this group already has a lesson at that time"
        )

    schedule = GroupSchedule(**data.model_dump())
    session.add(schedule)
    await session.commit()
    await session.refresh(schedule)
    return schedule


async def update_group_schedule(session: AsyncSession, schedule_id: int, data: GroupScheduleUpdateSchema):
    result = await session.execute(select(GroupSchedule).where(GroupSchedule.id == schedule_id))
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group schedule not found"
        )

    today = date.today()
    if data.date <= today:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Wrong date: date should be at least tomorrow ({today + timedelta(days=1)})"
        )

    if data.start_time >= data.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong time: end time should be greater than start time"
        )

    existing = await get_group_by_id(session, data.group_id)

    existing = await get_cabinet_by_id(session, data.cabinet_id)

    conflict_type = await check_schedule_conflict(session, data, schedule_id=schedule_id)
    if conflict_type == "cabinet":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Schedule conflict detected: this cabinet already has a lesson at that time"
        )
    elif conflict_type == "group":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Schedule conflict detected: this group already has a lesson at that time"
        )

    for field, value in data.model_dump().items():
        setattr(schedule, field, value)

    await session.commit()
    await session.refresh(schedule)
    return schedule


async def get_group_schedule_by_id(session: AsyncSession, schedule_id: int):
    result = await session.execute(select(GroupSchedule).where(GroupSchedule.id == schedule_id))
    group_schedule = result.scalar_one_or_none()
    if not group_schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group schedule not found")
    return group_schedule


async def get_group_schedules_by_group_id(session: AsyncSession, group_id: int):
    existing = await get_group_by_id(session, group_id)

    result = await session.execute(
        select(GroupSchedule)
        .where(
            GroupSchedule.group_id == group_id
        )
    )
    return result.scalars().all()


async def get_all_group_schedules(session: AsyncSession):
    result = await session.execute(select(GroupSchedule))
    return result.scalars().all()
