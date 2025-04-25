from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User
    from .category_level import CategoryLevel
    from .group import Group
    from .practice_schedule import PracticeSchedule


class Student(Base):
    __tablename__ = 'student'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete="CASCADE"),
        unique=True,
    )
    category_level_id: Mapped[int] = mapped_column(ForeignKey('category_level.id', ondelete="CASCADE"))
    group_id: Mapped[int | None] = mapped_column(ForeignKey('group.id', ondelete="SET NULL"))

    user: Mapped["User"] = relationship(back_populates="student")
    category_level: Mapped["CategoryLevel"] = relationship(back_populates="students")
    group: Mapped["Group"] = relationship(back_populates="students")
    practice_schedules: Mapped[list["PracticeSchedule"]] = relationship(back_populates="student")
