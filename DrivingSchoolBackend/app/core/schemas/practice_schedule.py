from pydantic import BaseModel, Field

from datetime import date as dt, timedelta, date
from datetime import time

from core.schemas.student import StudentReadSchema


class PracticeScheduleSchema(BaseModel):
    date: dt = Field(dt.today() + timedelta(days=1))
    start_time: time = Field(time(hour=10, minute=0), ge=time(hour=6, minute=0), le=time(hour=22, minute=30))
    end_time: time = Field(time(hour=12, minute=0), ge=time(hour=6, minute=30), le=time(hour=23, minute=0))
    instructor_id: int
    vehicle_id: int
    student_id: int


class PracticeScheduleCreateSchema(PracticeScheduleSchema):
    pass


class PracticeScheduleUpdateSchema(PracticeScheduleSchema):
    pass


class PracticeScheduleReadSchema(PracticeScheduleSchema):
    id: int


class PracticeScheduleButchCreateSchema(BaseModel):
    student_id: int
    instructor_id: int
    start_date: date = date.today() + timedelta(days=1)
    end_date: date = date.today() + timedelta(days=30)
    schedules_per_day: int = 1
    include_weekends: bool = False


class StudentForScheduleSchema(BaseModel):
    id: int
    instructor_id: int


class ExistingPracticeScheduleSchema(PracticeScheduleSchema):
    pass
