from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .group_schedule import GroupSchedule


class Cabinet(Base):
    __tablename__ = 'cabinet'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(16), unique=True)

    group_schedules: Mapped[list["GroupSchedule"]] = relationship(back_populates="cabinet")
