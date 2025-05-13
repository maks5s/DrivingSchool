from sqlalchemy import select, func, literal
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Instructor, Student, Group, Vehicle, Cabinet, CategoryLevel


async def get_statistics(session: AsyncSession):
    instructors_count = await session.scalar(select(func.count()).select_from(Instructor))
    students_count = await session.scalar(select(func.count()).select_from(Student))
    groups_count = await session.scalar(select(func.count()).select_from(Group))
    vehicles_count = await session.scalar(select(func.count()).select_from(Vehicle))
    cabinets_count = await session.scalar(select(func.count()).select_from(Cabinet))
    category_levels_count = await session.scalar(select(func.count()).select_from(CategoryLevel))

    res = await session.execute(
        select(
            func.concat(
                CategoryLevel.category,
                literal(" ("),
                CategoryLevel.transmission,
                literal(")")
            ),
            func.count(Student.id)
        )
        .join(Student, Student.category_level_id == CategoryLevel.id)
        .group_by(CategoryLevel.category, CategoryLevel.transmission)
    )
    students_per_category = [{"category_name": name, "count": count} for name, count in res.all()]

    res = await session.execute(
        select(
            func.concat(
                CategoryLevel.category,
                literal(" ("),
                CategoryLevel.transmission,
                literal(")")
            ),
            func.count(Group.id))
        .join(Group, Group.category_level_id == CategoryLevel.id)
        .group_by(CategoryLevel.category, CategoryLevel.transmission)
    )
    groups_per_category = [{"category_name": name, "count": count} for name, count in res.all()]

    return {
        "instructors_count": instructors_count,
        "students_count": students_count,
        "groups_count": groups_count,
        "vehicles_count": vehicles_count,
        "cabinets_count": cabinets_count,
        "category_levels_count": category_levels_count,
        "students_per_category": students_per_category,
        "groups_per_category": groups_per_category
    }