from pydantic import BaseModel
from datetime import date


class CategoryLevelProfileSchema(BaseModel):
    category: str
    transmission: str


class ProfileSchema(BaseModel):
    last_name: str
    first_name: str
    patronymic: str | None
    username: str
    phone_number: str
    birthday: date


class AdminProfileSchema(ProfileSchema):
    pass


class StudentProfileSchema(ProfileSchema, CategoryLevelProfileSchema):
    group: str


class InstructorProfileSchema(ProfileSchema):
    work_started_date: date
    categories: list[CategoryLevelProfileSchema]
