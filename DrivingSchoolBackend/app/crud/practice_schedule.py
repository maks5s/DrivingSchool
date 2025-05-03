from datetime import date, timedelta

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from core.config import settings
from core.models import PracticeSchedule
from core.schemas.group_schedule import ExistingGroupScheduleSchema
from core.schemas.practice_schedule import PracticeScheduleSchema, PracticeScheduleCreateSchema, \
    PracticeScheduleUpdateSchema, PracticeScheduleButchCreateSchema, StudentForScheduleSchema
from crud.category_level import get_category_level_by_id
from crud.instructor import get_instructor_by_id
from crud.student import get_student_by_id
from crud.vehicle import get_vehicle_by_id, get_all_vehicles_by_category_level
from schedule_generators.practice_schedule import generate_practice_schedule


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

    from crud.group_schedule import get_max_schedule_date_by_group_id
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

    from crud.group_schedule import get_max_schedule_date_by_group_id
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


async def get_all_practice_schedules_by_instructor_id_for_dates(
    session: AsyncSession,
    instructor_id: int,
    start_date: date,
    end_date: date
):
    result = await session.execute(
        select(PracticeSchedule)
        .where(
            and_(
                PracticeSchedule.instructor_id == instructor_id,
                PracticeSchedule.date >= start_date,
                PracticeSchedule.date <= end_date
            )
        )
    )
    return result.scalars().all()


async def get_all_practice_schedules_by_vehicle_id_for_dates(
    session: AsyncSession,
    vehicle_id: int,
    start_date: date,
    end_date: date
):
    result = await session.execute(
        select(PracticeSchedule)
        .where(
            and_(
                PracticeSchedule.vehicle_id == vehicle_id,
                PracticeSchedule.date >= start_date,
                PracticeSchedule.date <= end_date
            )
        )
    )
    return result.scalars().all()


async def create_butch_practice_schedules(
    session: AsyncSession,
    data: PracticeScheduleButchCreateSchema,
):
    today = date.today()
    if data.start_date <= today:
        raise Exception(f"Wrong date: date should be at least tomorrow ({today + timedelta(days=1)})")

    student = await get_student_by_id(session, data.student_id)

    existing = await get_instructor_by_id(session, data.instructor_id)

    start_time = settings.working_info.working_start_time
    end_time = settings.working_info.working_end_time
    category_level = await get_category_level_by_id(session, student.category_level_id)
    schedule_duration = category_level.category_level_info.practice_lessons_duration
    schedule_count = category_level.category_level_info.practice_lessons_count

    existing = list(await get_practice_schedules_by_student_id(session, student.id))
    existing_count = len(existing)
    if existing_count == schedule_count:
        raise Exception(f"Student already has {schedule_count} practice schedules")
    elif existing_count is not None:
        schedule_count = schedule_count - existing_count

    vehicles = await get_all_vehicles_by_category_level(session, student.category_level_id)
    if not vehicles:
        raise Exception("Could not find any vehicles for this category level")
    vehicle_ids = [vec.id for vec in vehicles]

    from crud.group_schedule import get_max_schedule_date_by_group_id
    max_group_schedule_date = await get_max_schedule_date_by_group_id(session, student.group_id)
    if not max_group_schedule_date:
        raise Exception("Student has no group schedules, cannot create practice schedules")
    elif max_group_schedule_date >= data.start_date:
        raise Exception(
            f"Wrong date: date should be at least the next day after student`s last group schedule "
            f"({max_group_schedule_date})"
        )

    from crud.group_schedule import get_all_group_schedules_by_instructor_id_for_dates
    group_schedules = list(await get_all_group_schedules_by_instructor_id_for_dates(
        session, data.instructor_id, data.start_date, data.end_date
    ))
    existing_group_schedules = []
    for group_schedule in group_schedules:
        existing_group_schedules.append(ExistingGroupScheduleSchema(
            date=group_schedule.date,
            start_time=group_schedule.start_time,
            end_time=group_schedule.end_time,
            group_id=group_schedule.group_id,
            cabinet_id=group_schedule.cabinet_id,
            instructor_id=data.instructor_id
        ))

    existing_practice_schedules = list(await get_all_practice_schedules_by_instructor_id_for_dates(
        session, data.instructor_id, data.start_date, data.end_date
    ))

    for vehicle_id in vehicle_ids:
        existing_practice_schedules.extend(list(await get_all_practice_schedules_by_vehicle_id_for_dates(
            session, vehicle_id, data.start_date, data.end_date
        )))

    result = generate_practice_schedule(
        student=StudentForScheduleSchema(id=student.id, instructor_id=data.instructor_id),
        vehicle_ids=vehicle_ids,
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

        schedule = PracticeSchedule(**item.model_dump())
        session.add(schedule)
        await session.commit()

    return {"success": True, "detail": "Created practice schedules"}
