from pydantic import BaseModel, Field

from datetime import date as dt, timedelta, date
from datetime import time


class GroupScheduleSchema(BaseModel):
    date: dt = Field(dt.today() + timedelta(days=1))
    start_time: time = Field(time(hour=10, minute=0), ge=time(hour=6, minute=0), le=time(hour=20, minute=0))
    end_time: time = Field(time(hour=12, minute=0), ge=time(hour=6, minute=30), le=time(hour=23, minute=0))
    group_id: int
    cabinet_id: int


class GroupScheduleCreateSchema(GroupScheduleSchema):
    pass


class GroupScheduleUpdateSchema(GroupScheduleSchema):
    pass


class GroupScheduleReadSchema(GroupScheduleSchema):
    id: int


class ExistingGroupScheduleSchema(GroupScheduleSchema):
    instructor_id: int


class GroupForScheduleSchema(BaseModel):
    id: int
    instructor_id: int


class GroupScheduleButchCreateSchema(BaseModel):
    group_id: int
    start_date: date = date.today() + timedelta(days=1)
    end_date: date = date.today() + timedelta(days=30)
    schedules_per_day: int = 1
    include_weekends: bool = False
