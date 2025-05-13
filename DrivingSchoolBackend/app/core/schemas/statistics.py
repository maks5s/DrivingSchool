from pydantic import BaseModel


class CategoryCount(BaseModel):
    category_name: str
    count: int


class StatisticsResponseSchema(BaseModel):
    instructors_count: int
    students_count: int
    groups_count: int
    vehicles_count: int
    cabinets_count: int
    category_levels_count: int
    students_per_category: list[CategoryCount]
    groups_per_category: list[CategoryCount]
