from datetime import date

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .student import Student
    from .instructor import Instructor


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[str]
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    patronymic: Mapped[str | None] = mapped_column(String(50))
    birthday: Mapped[date]
    phone_number: Mapped[str] = mapped_column(String(15), unique=True)

    student: Mapped["Student"] = relationship(back_populates="user")
    instructor: Mapped["Instructor"] = relationship(back_populates="user")
