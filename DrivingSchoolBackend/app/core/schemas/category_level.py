from datetime import time

from pydantic import BaseModel, Field


class CategoryLevelInfoSchema(BaseModel):
    theory_lessons_count: int = Field(20, ge=1, le=100)
    practice_lessons_count: int = Field(20, ge=1, le=100)
    theory_lessons_duration: time = time(hour=2)
    practice_lessons_duration: time = time(hour=2)
    minimum_age_to_get: int = Field(18, ge=16, le=100)


class CategoryLevelBaseSchema(BaseModel):
    category: str = Field(..., max_length=10)
    transmission: str = Field(..., max_length=32)
    description: str = Field(..., max_length=255)


class CategoryLevelCreateSchema(CategoryLevelBaseSchema, CategoryLevelInfoSchema):
    pass


class CategoryLevelUpdateSchema(CategoryLevelCreateSchema):
    pass


class CategoryLevelReadSchema(CategoryLevelBaseSchema):
    id: int
    category_level_info: CategoryLevelInfoSchema
