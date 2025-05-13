from datetime import date, timedelta
from random import randint, choice

from faker import Faker
from fastapi import HTTPException, status
from pydantic import ValidationError
from sqlalchemy import select, and_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.models import CategoryLevel, Cabinet, Vehicle, User, Instructor, InstructorCategoryLevel, CategoryLevelInfo, \
    Group, Student
from auth.utils import hash_password
from core.schemas.cabinet import CabinetCreateSchema
from core.schemas.category_level import CategoryLevelCreateSchema
from core.schemas.group import GroupCreateSchema
from core.schemas.group_schedule import GroupScheduleButchCreateSchema
from core.schemas.instructor import InstructorCreateSchema
from core.schemas.practice_schedule import PracticeScheduleButchCreateSchema
from core.schemas.student import StudentCreateSchema
from core.schemas.user import UserSchema
from core.schemas.vehicle import VehicleCreateSchema
from crud.category_level import get_all_category_levels, get_category_level_by_id
from crud.group_schedule import create_butch_group_schedules, get_max_schedule_date_by_group_id
from crud.instructor import get_instructors_by_category_level_id
from crud.practice_schedule import create_butch_practice_schedules
from crud.user import get_user_by_username, get_user_by_phone_number


fake = Faker()


async def load_initial_data(
    data: dict,
    session: AsyncSession
):

    try:
        # === CategoryLevels ===
        category_level_map = {}
        category_level_age_map = {}
        for c in data["category_levels"]:
            cl = CategoryLevelCreateSchema(
                category=c["category"],
                transmission=c["transmission"],
                description=c["description"],
                theory_lessons_count=c["theory_lessons_count"],
                practice_lessons_count=c["practice_lessons_count"],
                theory_lessons_duration=c["theory_lessons_duration"],
                practice_lessons_duration=c["practice_lessons_duration"],
                minimum_age_to_get=c["minimum_age_to_get"],
            )

            result = await session.execute(
                select(CategoryLevel).where(
                    and_(
                        CategoryLevel.category == cl.category,
                        CategoryLevel.transmission == cl.transmission
                    )
                )
            )
            if result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Category level with this category and transmission already exists: "
                           f"{cl.category} {cl.transmission}"
                )

            category_level = CategoryLevel(
                category=cl.category,
                transmission=cl.transmission,
                description=cl.description,
            )
            session.add(category_level)
            await session.flush()

            info = CategoryLevelInfo(
                category_level_id=category_level.id,
                theory_lessons_count=cl.theory_lessons_count,
                practice_lessons_count=cl.practice_lessons_count,
                theory_lessons_duration=cl.theory_lessons_duration,
                practice_lessons_duration=cl.practice_lessons_duration,
                minimum_age_to_get=cl.minimum_age_to_get,
            )
            session.add(info)

            category_level_map[(category_level.category, category_level.transmission)] = category_level.id
            category_level_age_map[category_level.id] = info.minimum_age_to_get

        # === Cabinets ===
        for cab in data["cabinets"]:
            c = CabinetCreateSchema(
                name=cab["name"]
            )

            result = await session.execute(
                select(Cabinet)
                .where(Cabinet.name == c.name)
            )
            if result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cabinet with this name already exists: {c.name}"
                )

            cabinet = Cabinet(
                name=c.name
            )
            session.add(cabinet)

        # === Vehicles ===
        for v in data["vehicles"]:
            cat_id = category_level_map[(v["category"], v["transmission"])]

            vec = VehicleCreateSchema(
                brand=v["brand"],
                model=v["model"],
                manufacture_year=v["manufacture_year"],
                license_plate=v["license_plate"],
                fuel_type=v["fuel_type"],
                category_level_id=cat_id
            )

            result = await session.execute(
                select(Vehicle)
                .where(Vehicle.license_plate == vec.license_plate)
            )
            if result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Vehicle with this license plate already exists: {vec.license_plate}"
                )

            vehicle = Vehicle(
                brand=vec.brand,
                model=vec.model,
                manufacture_year=vec.manufacture_year,
                license_plate=vec.license_plate,
                fuel_type=vec.fuel_type,
                category_level_id=vec.category_level_id
            )
            session.add(vehicle)

        # === Instructors ===
        for inst in data["instructors"]:

            i = InstructorCreateSchema(
                user=UserSchema(
                    username=inst["username"],
                    first_name=inst["first_name"],
                    last_name=inst["last_name"],
                    patronymic=inst.get("patronymic"),
                    birthday=date.fromisoformat(inst["birthday"]),
                    phone_number=inst["phone_number"]
                ),
                work_started_date=date.fromisoformat(inst["work_started_date"]),
                password=inst["password"]
            )

            existing = await get_user_by_username(session, i.user.username)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User with this username already exists: {i.user.username}"
                )

            existing = await get_user_by_phone_number(session, i.user.phone_number)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User with this phone number already exists: {i.user.phone_number}"
                )

            user = User(
                username=i.user.username,
                first_name=i.user.first_name,
                last_name=i.user.last_name,
                patronymic=i.user.patronymic,
                birthday=i.user.birthday,
                phone_number=i.user.phone_number,
                hashed_password=hash_password(i.password),
            )
            session.add(user)
            await session.flush()

            instructor = Instructor(
                id=user.id,
                work_started_date=i.work_started_date,
            )
            session.add(instructor)

            create_query = text(f"""
                    CREATE USER "{i.user.username}" WITH PASSWORD '{i.password}';
                """)
            grant_query = text(f"""
                    GRANT instructor_role TO "{i.user.username}";
                """)
            await session.execute(create_query)
            await session.execute(grant_query)

            today = date.today()

            for c in inst["categories"]:
                cat_id = category_level_map[(c["category"], c["transmission"])]

                birthday = i.user.birthday
                age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))

                min_age = category_level_age_map[cat_id]
                if age < min_age:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Instructor '{i.user.username}' must be at least {min_age} "
                               f"years old to enroll in this category level"
                    )

                link = InstructorCategoryLevel(
                    instructor_id=instructor.id,
                    category_level_id=cat_id
                )
                session.add(link)

        await session.commit()

        return {"detail": "Data loaded successfully"}
    except ValidationError as e:
        messages = [f"{error['loc'][0]}: {error['msg']}" for error in e.errors()]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=messages
        )
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


async def generate_test_data(session: AsyncSession):
    category_levels = await get_all_category_levels(session)
    category_levels_ids = [cl.id for cl in category_levels]

    # === Groups ===
    group_list = []
    student_list = []
    group_count = 2
    for i in range(group_count):
        cat_id = choice(category_levels_ids)

        inst_ids = [i.id for i in await get_instructors_by_category_level_id(session, cat_id)]

        gr = GroupCreateSchema(
            name=f"Group {fake.bothify(text='??-###')}",
            created_date=(date.today() - timedelta(days=randint(1, 30))),
            category_level_id=cat_id,
            instructor_id=choice(inst_ids),
        )

        result = await session.execute(select(Group).where(Group.name == gr.name))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Group with this name already exists: {gr.name}"
            )

        group = Group(**gr.model_dump())
        session.add(group)
        await session.flush()

        group_list.append(group.id)

        # === Students ===
        student_count = randint(14, 23)
        category_level = await get_category_level_by_id(session, cat_id)
        for j in range(student_count):
            username = f"{fake.first_name()}{fake.bothify(text='??')}"

            stud = StudentCreateSchema(
                user=UserSchema(
                    username=username,
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    patronymic=fake.first_name(),
                    birthday=fake.date_of_birth(
                        minimum_age=category_level.category_level_info.minimum_age_to_get,
                        maximum_age=category_level.category_level_info.minimum_age_to_get + 50
                    ),
                    phone_number=fake.msisdn()
                ),
                password=username,
                category_level_id=cat_id,
                group_id=group.id,
            )

            existing = await get_user_by_username(session, stud.user.username)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User with this username already exists: {stud.user.username}"
                )

            existing = await get_user_by_phone_number(session, stud.user.phone_number)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User with this phone number already exists: {stud.user.phone_number}"
                )

            user = User(
                username=stud.user.username,
                first_name=stud.user.first_name,
                last_name=stud.user.last_name,
                patronymic=stud.user.patronymic,
                birthday=stud.user.birthday,
                phone_number=stud.user.phone_number,
                hashed_password=hash_password(stud.password),
            )
            session.add(user)
            await session.flush()

            student = Student(
                id=user.id,
                category_level_id=stud.category_level_id,
                group_id=stud.group_id
            )
            session.add(student)

            create_query = text(f"""
                    CREATE USER "{stud.user.username}" WITH PASSWORD '{stud.password}';
                """)
            grant_query = text(f"""
                    GRANT student_role TO "{stud.user.username}";
                """)
            await session.execute(create_query)
            await session.execute(grant_query)

            student_list.append((student.id, stud.category_level_id, stud.group_id))

    await session.commit()

    # === Group schedule ===
    for group_id in group_list:
        start_date = date.today() + timedelta(days=randint(1, 30))
        end_date = start_date + timedelta(days=randint(30, 60))

        while True:
            gr_sch = GroupScheduleButchCreateSchema(
                group_id=group_id,
                start_date=start_date,
                end_date=end_date,
                schedules_per_day=randint(1, 3),
                include_weekends=choice([True, False])
            )
            try:
                await create_butch_group_schedules(session, gr_sch)
                break
            except Exception as e:
                if "Not all schedules can be generated" in str(e):
                    end_date += timedelta(days=30)
                else:
                    raise e

    # === Practice schedule ===
    for student_id, cat_id, group_id in student_list:
        inst_ids = [i.id for i in await get_instructors_by_category_level_id(session, cat_id)]

        max_group_schedule_date = await get_max_schedule_date_by_group_id(session, group_id)
        start_date = max_group_schedule_date + timedelta(days=randint(1, 10))
        end_date = start_date + timedelta(days=randint(30, 60))

        while True:
            pr_sch = PracticeScheduleButchCreateSchema(
                student_id=student_id,
                instructor_id=choice(inst_ids),
                start_date=start_date,
                end_date=end_date,
                schedules_per_day=randint(1, 3),
                include_weekends=choice([True, False])
            )
            try:
                await create_butch_practice_schedules(session, pr_sch)
                break
            except Exception as e:
                if "Not all schedules can be generated" in str(e):
                    end_date += timedelta(days=30)
                else:
                    raise e

    return {"detail": "Test data has generated"}


async def get_export_data(session: AsyncSession):
    groups_data = []

    result = await session.execute(
        select(Group)
        .options(
            selectinload(Group.category_level),
            selectinload(Group.instructor).selectinload(Instructor.user),
            selectinload(Group.students).selectinload(Student.user),
        )
    )
    groups = result.scalars().all()

    for group in groups:
        category_level = group.category_level
        instructor = group.instructor
        students = group.students

        group_info = {
            "group_name": group.name,
            "created_date": group.created_date.isoformat(),
            "category_level": {
                "category": category_level.category,
                "transmission": category_level.transmission,
            },
            "instructor": {
                "first_name": instructor.user.first_name,
                "last_name": instructor.user.last_name,
                "patronymic": instructor.user.patronymic,
                "phone_number": instructor.user.phone_number
            },
            "students": [
                {
                    "first_name": s.user.first_name,
                    "last_name": s.user.last_name,
                    "patronymic": s.user.patronymic,
                    "birthday": s.user.birthday.isoformat(),
                    "phone_number": s.user.phone_number
                }
                for s in students
            ]
        }
        groups_data.append(group_info)

    return groups_data
