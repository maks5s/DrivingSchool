from pydantic import BaseModel, Field

from core.schemas.user import UserSchema


class AdminSchema(BaseModel):
    user: UserSchema


class AdminUpdateSchema(AdminSchema):
    password: str | None = Field(None, min_length=5)
