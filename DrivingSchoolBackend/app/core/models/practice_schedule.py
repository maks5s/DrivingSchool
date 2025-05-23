import datetime
from datetime import time

from sqlalchemy import ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .instructor import Instructor
    from .vehicle import Vehicle
    from .student import Student


class PracticeSchedule(Base):
    __tablename__ = 'practice_schedule'

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime.date] = mapped_column(index=True)
    start_time: Mapped[time] = mapped_column(index=True)
    end_time: Mapped[time] = mapped_column(index=True)
    instructor_id: Mapped[int] = mapped_column(ForeignKey('instructor.id', ondelete="CASCADE"))
    vehicle_id: Mapped[int] = mapped_column(ForeignKey('vehicle.id', ondelete="CASCADE"))
    student_id: Mapped[int] = mapped_column(ForeignKey('student.id', ondelete="CASCADE"))

    instructor: Mapped["Instructor"] = relationship(back_populates="practice_schedules")
    vehicle: Mapped["Vehicle"] = relationship(back_populates="practice_schedules")
    student: Mapped["Student"] = relationship(back_populates="practice_schedules")
