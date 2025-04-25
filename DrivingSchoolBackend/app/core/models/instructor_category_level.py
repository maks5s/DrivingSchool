from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .instructor import Instructor
    from .category_level import CategoryLevel


class InstructorCategoryLevel(Base):
    __tablename__ = 'instructor_category_level'

    instructor_id: Mapped[int] = mapped_column(
        ForeignKey('instructor.id', ondelete="CASCADE"),
        primary_key=True
    )
    category_level_id: Mapped[int] = mapped_column(
        ForeignKey('category_level.id', ondelete="CASCADE"),
        primary_key=True
    )

    instructor: Mapped["Instructor"] = relationship(back_populates="instructor_category_levels")
    category_level: Mapped["CategoryLevel"] = relationship(back_populates="instructor_category_levels")

    __table_args__ = (UniqueConstraint("instructor_id", "category_level_id"),)
