from datetime import date, timedelta

from pydantic import BaseModel, Field

from core.schemas.user import UserSchema


class InstructorBaseSchema(BaseModel):
    work_started_date: date = Field(
        date.today() - timedelta(days=1 * 365),
        le=date.today()
    )


class InstructorSchema(InstructorBaseSchema):
    user: UserSchema


class InstructorCreateSchema(InstructorSchema):
    password: str = Field(..., min_length=5)


class InstructorUpdateSchema(InstructorCreateSchema):
    password: str | None = Field(None, min_length=5)


class InstructorReadSchema(InstructorSchema):
    id: int
