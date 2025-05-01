from datetime import date

from pydantic import BaseModel, Field


class GroupSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    created_date: date = Field(date.today(), le=date.today())
    category_level_id: int
    instructor_id: int


class GroupCreateSchema(GroupSchema):
    pass


class GroupUpdateSchema(GroupSchema):
    pass


class GroupReadSchema(GroupSchema):
    id: int
