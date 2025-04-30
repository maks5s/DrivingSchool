from datetime import date

from pydantic import BaseModel, Field


class UserSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    first_name: str = Field(..., min_length=1,  max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    patronymic: str | None = Field(None, min_length=1, max_length=50)
    birthday: date
    phone_number: str = Field(..., max_length=15, min_length=10)


class UserCreateSchema(UserSchema):
    password: str = Field(..., min_length=5)


class UserReadSchema(UserSchema):
    id: int


class UserJWTSchema(BaseModel):
    id: int
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=5)
    role: str


class UserWithRoleReadSchema(UserReadSchema):
    role: str
