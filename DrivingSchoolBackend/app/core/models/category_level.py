from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .student import Student
    from .category_level_info import CategoryLevelInfo
    from .instructor_category_level import InstructorCategoryLevel
    from .vehicle import Vehicle
    from .group import Group


class CategoryLevel(Base):
    __tablename__ = 'category_level'

    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[str] = mapped_column(String(10))
    transmission: Mapped[str] = mapped_column(String(32))
    description: Mapped[str] = mapped_column(String(255))

    category_level_info: Mapped["CategoryLevelInfo"] = relationship(back_populates="category_level")
    students: Mapped[list["Student"]] = relationship(back_populates="category_level")
    instructor_category_levels: Mapped[list["InstructorCategoryLevel"]] = relationship(back_populates="category_level")
    vehicles: Mapped[list["Vehicle"]] = relationship(back_populates="category_level")
    groups: Mapped[list["Group"]] = relationship(back_populates="category_level")
