from datetime import date, timedelta

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy.orm import joinedload

from core.config import settings
from core.models import GroupSchedule, Group, Student
from core.schemas.group_schedule import GroupScheduleCreateSchema, GroupScheduleUpdateSchema, GroupScheduleSchema, \
    GroupScheduleButchCreateSchema, ExistingGroupScheduleSchema, GroupForScheduleSchema
from core.schemas.profile_schedule import StudentProfileScheduleSchema, InstructorProfileScheduleSchema
from crud.cabinet import get_cabinet_by_id, get_all_cabinets
from crud.category_level import get_category_level_by_id
from crud.group import get_group_by_id
from crud.instructor import get_instructor_by_id
from schedule_generators.group_schedule import generate_group_schedule


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

    if cabinet_result.scalars().all():
        return "cabinet"
    if group_result.scalars().all():
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


async def get_all_group_schedules_by_instructor_id_for_dates(
    session: AsyncSession,
    instructor_id: int,
    start_date: date,
    end_date: date
):
    result = await session.execute(
        select(GroupSchedule)
        .options(joinedload(GroupSchedule.group))
        .join(GroupSchedule.group)
        .where(
            and_(
                Group.instructor_id == instructor_id,
                GroupSchedule.date >= start_date,
                GroupSchedule.date <= end_date
            )
        )
    )
    return result.scalars().all()


async def get_all_group_schedules_by_cabinet_id_for_dates(
    session: AsyncSession,
    cabinet_id: int,
    start_date: date,
    end_date: date
):
    result = await session.execute(
        select(GroupSchedule)
        .where(
            and_(
                GroupSchedule.cabinet_id == cabinet_id,
                GroupSchedule.date >= start_date,
                GroupSchedule.date <= end_date
            )
        )
    )
    return result.scalars().all()


async def get_max_schedule_date_by_group_id(session: AsyncSession, group_id: int):
    existing = await get_group_by_id(session, group_id)

    result = await session.execute(
        select(func.max(GroupSchedule.date))
        .where(GroupSchedule.group_id == group_id)
    )
    return result.scalar_one_or_none()


async def get_group_schedules_by_student_id_and_date(session: AsyncSession, student_id: int, date: date):
    result = await session.execute(
        select(GroupSchedule)
        .join(GroupSchedule.group)
        .join(Group.students)
        .options(joinedload(GroupSchedule.cabinet))
        .where(Student.id == student_id, GroupSchedule.date == date)
    )
    schedules = result.scalars().all()

    return [
        StudentProfileScheduleSchema(
            start_time=s.start_time,
            end_time=s.end_time,
            type="Group",
            extra=s.cabinet.name
        )
        for s in schedules
    ]


async def get_group_schedules_by_instructor_and_date(session, instructor_id: int, date: date):
    result = await session.execute(
        select(GroupSchedule)
        .options(
            joinedload(GroupSchedule.cabinet),
            joinedload(GroupSchedule.group)
        )
        .join(GroupSchedule.group)
        .where(GroupSchedule.date == date, GroupSchedule.group.has(instructor_id=instructor_id))
    )
    schedules = result.scalars().all()

    return [
        InstructorProfileScheduleSchema(
            start_time=s.start_time,
            end_time=s.end_time,
            type="Group",
            extra=f"{s.cabinet.name} — {s.group.name}"
        )
        for s in schedules
    ]


async def create_butch_practice_schedules(
    session: AsyncSession,
    data: GroupScheduleButchCreateSchema,
):
    today = date.today()
    if data.start_date <= today:
        raise Exception(f"Wrong date: date should be at least tomorrow ({today + timedelta(days=1)})")

    group = await get_group_by_id(session, data.group_id)
    existing = await get_instructor_by_id(session, group.instructor_id)

    start_time = settings.working_info.working_start_time
    end_time = settings.working_info.working_end_time
    category_level = await get_category_level_by_id(session, group.category_level_id)
    schedule_duration = category_level.category_level_info.theory_lessons_duration
    schedule_count = category_level.category_level_info.theory_lessons_count

    existing = list(await get_group_schedules_by_group_id(session, group.id))
    existing_count = len(existing)
    if existing_count == schedule_count:
        raise Exception(f"Group already has {schedule_count} practice schedules")
    elif existing_count is not None:
        schedule_count = schedule_count - existing_count

    cabinets = await get_all_cabinets(session)
    if not cabinets:
        raise Exception("Could not find any cabinets")
    cabinet_ids = [cab.id for cab in cabinets]

    group_schedules = list(await get_all_group_schedules_by_instructor_id_for_dates(
        session, group.instructor_id, data.start_date, data.end_date
    ))
    for cabinet_id in cabinet_ids:
        group_schedules.extend(list(await get_all_group_schedules_by_cabinet_id_for_dates(
            session, cabinet_id, data.start_date, data.end_date
        )))

    existing_group_schedules = []
    for group_schedule in group_schedules:
        existing_group_schedules.append(ExistingGroupScheduleSchema(
            date=group_schedule.date,
            start_time=group_schedule.start_time,
            end_time=group_schedule.end_time,
            group_id=group_schedule.group_id,
            cabinet_id=group_schedule.cabinet_id,
            instructor_id=group.instructor_id
        ))

    from crud.practice_schedule import get_all_practice_schedules_by_instructor_id_for_dates
    existing_practice_schedules = list(await get_all_practice_schedules_by_instructor_id_for_dates(
        session, group.instructor_id, data.start_date, data.end_date
    ))

    result = generate_group_schedule(
        group=GroupForScheduleSchema(id=group.id, instructor_id=group.instructor_id),
        cabinet_ids=cabinet_ids,
        existing_group_schedules=existing_group_schedules,
        existing_practice_schedules=existing_practice_schedules,
        start_date=data.start_date,
        end_date=data.end_date,
        schedule_start_time=start_time,
        schedule_end_time=end_time,
        schedule_duration=schedule_duration,
        schedule_count=schedule_count,
        schedules_per_day=data.schedules_per_day,
        include_weekends=data.include_weekends,
    )
    for item in result:
        print(item)

        schedule = GroupSchedule(**item.model_dump())
        session.add(schedule)
        await session.commit()

    return {"success": True, "detail": "Created group schedules"}
