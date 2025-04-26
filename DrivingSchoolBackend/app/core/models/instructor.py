from datetime import date

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User
    from .instructor_category_level import InstructorCategoryLevel
    from .group import Group
    from .practice_schedule import PracticeSchedule


class Instructor(Base):
    __tablename__ = 'instructor'

    # id: Mapped[int] = mapped_column(primary_key=True)
    id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete="CASCADE"),
        unique=True,
        primary_key=True,
    )
    work_started_date: Mapped[date]
    # user_id: Mapped[int] = mapped_column(
    #     ForeignKey('user.id', ondelete="CASCADE"),
    #     unique=True,
    # )

    user: Mapped["User"] = relationship(back_populates="instructor")
    instructor_category_levels: Mapped[list["InstructorCategoryLevel"]] = relationship(back_populates="instructor")
    groups: Mapped[list["Group"]] = relationship(back_populates="instructor")
    # group_schedules: Mapped[list["GroupSchedule"]] = relationship(back_populates="instructor")
    practice_schedules: Mapped[list["PracticeSchedule"]] = relationship(back_populates="instructor")
