from datetime import date, timedelta

from pydantic import BaseModel, Field, field_validator

from core.config import USERNAME_REGEX, PASSWORD_REGEX


class UserSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    first_name: str = Field(..., min_length=1,  max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    patronymic: str | None = Field(None, min_length=1, max_length=50)
    birthday: date = Field(
        date.today() - timedelta(days=18*365),
        le=date.today() - timedelta(days=16*365)
    )
    phone_number: str = Field(..., max_length=15, min_length=10)

    @field_validator("username", mode='before')
    def validate_username(cls, v):
        if not USERNAME_REGEX.match(v):
            raise ValueError("Username must contain only letters, digits, and underscores (3–30 chars)")
        return v

    @field_validator("password", mode="before")
    def validate_password(cls, v):
        if not PASSWORD_REGEX.match(v):
            raise ValueError("Password must contain only letters, digits, and underscores (5–50 chars)")
        return v


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
