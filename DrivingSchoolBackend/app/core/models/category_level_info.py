from datetime import time

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .category_level import CategoryLevel


class CategoryLevelInfo(Base):
    __tablename__ = 'category_level_info'

    category_level_id: Mapped[int] = mapped_column(
        ForeignKey('category_level.id', ondelete="CASCADE"),
        primary_key=True,
        unique=True,
    )
    theory_lessons_count: Mapped[int]
    practice_lessons_count: Mapped[int]
    theory_lessons_duration: Mapped[time]
    practice_lessons_duration: Mapped[time]
    minimum_age_to_get: Mapped[int]

    category_level: Mapped["CategoryLevel"] = relationship(back_populates="category_level_info")
