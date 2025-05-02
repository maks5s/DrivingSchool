from datetime import date, timedelta

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from core.models import PracticeSchedule
from core.schemas.practice_schedule import PracticeScheduleSchema, PracticeScheduleCreateSchema, \
    PracticeScheduleUpdateSchema
from crud.group_schedule import get_max_schedule_date_by_group_id
from crud.instructor import get_instructor_by_id
from crud.student import get_student_by_id
from crud.vehicle import get_vehicle_by_id


async def check_schedule_conflict(session: AsyncSession, data: PracticeScheduleSchema, schedule_id: int | None = None):
    filters = [
        PracticeSchedule.date == data.date,
        or_(
            and_(PracticeSchedule.start_time <= data.start_time, PracticeSchedule.end_time > data.start_time),
            and_(PracticeSchedule.start_time < data.end_time, PracticeSchedule.end_time >= data.end_time),
            and_(PracticeSchedule.start_time >= data.start_time, PracticeSchedule.end_time <= data.end_time),
        )
    ]
    if schedule_id:
        exclude_self = PracticeSchedule.id != schedule_id
    else:
        exclude_self = True

    # Instructor
    instructor_query = select(PracticeSchedule).where(
        and_(
            *filters,
            PracticeSchedule.instructor_id == data.instructor_id,
            exclude_self
        )
    )

    # Vehicle
    vehicle_query = select(PracticeSchedule).where(
        and_(
            *filters,
            PracticeSchedule.vehicle_id == data.vehicle_id,
            exclude_self
        )
    )

    # Student
    student_query = select(PracticeSchedule).where(
        and_(
            *filters,
            PracticeSchedule.student_id == data.student_id,
            exclude_self
        )
    )

    instructor_result = await session.execute(instructor_query)
    vehicle_result = await session.execute(vehicle_query)
    student_result = await session.execute(student_query)

    if instructor_result.scalars().all():
        return "instructor"
    if vehicle_result.scalars().all():
        return "vehicle"
    if student_result.scalars().all():
        return "student"
    return None


async def create_practice_schedule(session: AsyncSession, data: PracticeScheduleCreateSchema):
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

    existing = await get_instructor_by_id(session, data.instructor_id)

    existing = await get_vehicle_by_id(session, data.vehicle_id)

    student = await get_student_by_id(session, data.student_id)

    max_group_schedule_date = await get_max_schedule_date_by_group_id(session, student.group_id)
    if not max_group_schedule_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student has no group schedule, cannot create practice schedule"
        )
    elif max_group_schedule_date >= data.date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Wrong date: date should be at least the next day after last group schedule ({max_group_schedule_date})"
        )

    conflict_type = await check_schedule_conflict(session, data)
    if conflict_type == "instructor":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Schedule conflict detected: this instructor already has a lesson at that time"
        )
    elif conflict_type == "vehicle":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Schedule conflict detected: this vehicle already has a lesson at that time"
        )
    elif conflict_type == "student":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Schedule conflict detected: this student already has a lesson at that time"
        )

    schedule = PracticeSchedule(**data.model_dump())
    session.add(schedule)
    await session.commit()
    await session.refresh(schedule)
    return schedule


async def update_practice_schedule(session: AsyncSession, schedule_id: int, data: PracticeScheduleUpdateSchema):
    result = await session.execute(select(PracticeSchedule).where(PracticeSchedule.id == schedule_id))
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Practice schedule not found"
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

    existing = await get_instructor_by_id(session, data.instructor_id)

    existing = await get_vehicle_by_id(session, data.vehicle_id)

    student = await get_student_by_id(session, data.student_id)

    max_group_schedule_date = await get_max_schedule_date_by_group_id(session, student.group_id)
    if not max_group_schedule_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student has no group schedule, cannot update practice schedule"
        )
    elif max_group_schedule_date >= data.date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Wrong date: date should be at least the next day after last group schedule ({max_group_schedule_date})"
        )

    conflict_type = await check_schedule_conflict(session, data, schedule_id=schedule_id)
    if conflict_type == "instructor":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Schedule conflict detected: this instructor already has a lesson at that time"
        )
    elif conflict_type == "vehicle":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Schedule conflict detected: this vehicle already has a lesson at that time"
        )
    elif conflict_type == "student":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Schedule conflict detected: this student already has a lesson at that time"
        )

    for field, value in data.model_dump().items():
        setattr(schedule, field, value)

    await session.commit()
    await session.refresh(schedule)
    return schedule


async def get_practice_schedule_by_id(session: AsyncSession, schedule_id: int):
    result = await session.execute(select(PracticeSchedule).where(PracticeSchedule.id == schedule_id))
    practice_schedule = result.scalar_one_or_none()
    if not practice_schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Practice schedule not found")
    return practice_schedule


async def get_practice_schedules_by_student_id(session: AsyncSession, student_id: int):
    existing = await get_student_by_id(session, student_id)

    result = await session.execute(
        select(PracticeSchedule)
        .where(
            PracticeSchedule.student_id == student_id
        )
    )
    return result.scalars().all()


async def get_all_practice_schedules(session: AsyncSession):
    result = await session.execute(select(PracticeSchedule))
    return result.scalars().all()
