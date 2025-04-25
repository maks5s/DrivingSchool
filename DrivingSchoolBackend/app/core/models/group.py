from datetime import date

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .student import Student
    from .instructor import Instructor
    from .category_level import CategoryLevel
    from .group_schedule import GroupSchedule


class Group(Base):
    __tablename__ = 'group'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    created_date: Mapped[date]
    category_level_id: Mapped[int] = mapped_column(ForeignKey('category_level.id', ondelete="CASCADE"))
    instructor_id: Mapped[int | None] = mapped_column(ForeignKey('instructor.id', ondelete="SET NULL"))

    category_level: Mapped["CategoryLevel"] = relationship(back_populates="groups")
    instructor: Mapped["Instructor"] = relationship(back_populates="groups")
    students: Mapped[list["Student"]] = relationship(back_populates="group")
    group_schedules: Mapped[list["GroupSchedule"]] = relationship(back_populates="group")
