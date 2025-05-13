from pydantic import BaseModel, Field

from core.schemas.user import UserSchema


class StudentBaseSchema(BaseModel):
    category_level_id: int
    group_id: int


class StudentSchema(StudentBaseSchema):
    user: UserSchema


class StudentCreateSchema(StudentSchema):
    password: str = Field(..., min_length=5)


class StudentUpdateSchema(StudentCreateSchema):
    password: str | None = Field(None, min_length=5)


class StudentReadSchema(StudentSchema):
    id: int


class StudentPaginatedReadSchema(StudentReadSchema):
    has_schedule: bool
