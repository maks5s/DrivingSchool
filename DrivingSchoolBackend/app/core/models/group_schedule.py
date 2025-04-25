from datetime import date, time

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .group import Group
    from .cabinet import Cabinet


class GroupSchedule(Base):
    __tablename__ = 'group_schedule'

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date]
    start_time: Mapped[time]
    end_time: Mapped[time]
    group_id: Mapped[int] = mapped_column(ForeignKey('group.id', ondelete="CASCADE"))
    # instructor_id: Mapped[int] = mapped_column(ForeignKey('instructor.id', ondelete="CASCADE"))
    cabinet_id: Mapped[int] = mapped_column(ForeignKey('cabinet.id', ondelete="CASCADE"))

    group: Mapped["Group"] = relationship(back_populates="group_schedules")
    # instructor: Mapped["Instructor"] = relationship(back_populates="group_schedules")
    cabinet: Mapped["Cabinet"] = relationship(back_populates="group_schedules")
