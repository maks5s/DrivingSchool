from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .category_level import CategoryLevel
    from .practice_schedule import PracticeSchedule


class Vehicle(Base):
    __tablename__ = 'vehicle'

    id: Mapped[int] = mapped_column(primary_key=True)
    brand: Mapped[str] = mapped_column(String(50))
    model: Mapped[str] = mapped_column(String(50))
    manufacture_year: Mapped[int]
    license_plate: Mapped[str] = mapped_column(String(20))
    fuel_type: Mapped[str] = mapped_column(String(20))
    category_level_id: Mapped[int] = mapped_column(ForeignKey('category_level.id', ondelete="CASCADE"))

    category_level: Mapped["CategoryLevel"] = relationship(back_populates="vehicles")
    practice_schedules: Mapped[list["PracticeSchedule"]] = relationship(back_populates="vehicle")
