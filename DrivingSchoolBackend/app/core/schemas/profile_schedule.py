from pydantic import BaseModel
from datetime import time


class ProfileScheduleSchema(BaseModel):
    start_time: time
    end_time: time
    type: str
    extra: str


class InstructorProfileScheduleSchema(ProfileScheduleSchema):
    pass


class StudentProfileScheduleSchema(ProfileScheduleSchema):
    pass
