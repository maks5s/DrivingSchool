from datetime import date, timedelta, time, datetime
from pulp import LpProblem, LpVariable, LpBinary, lpSum, LpMaximize, PULP_CBC_CMD
from typing import List
from collections import defaultdict

from core.schemas.group_schedule import ExistingGroupScheduleSchema
from core.schemas.practice_schedule import PracticeScheduleSchema, StudentForScheduleSchema, \
    ExistingPracticeScheduleSchema


def has_time_conflict(start1, end1, start2, end2):
    return start1 < end2 and start2 < end1


def generate_practice_schedule(
    student: StudentForScheduleSchema,
    vehicle_ids: List[int],
    existing_group_schedules: List[ExistingGroupScheduleSchema],
    existing_practice_schedules: List[ExistingPracticeScheduleSchema],
    start_date: date = date.today() + timedelta(days=1),
    end_date: date = date.today() + timedelta(days=30),
    schedule_start_time: time = time(8, 0),
    schedule_end_time: time = time(18, 0),
    schedule_duration: time = time(2, 0),
    schedule_count=20,
    schedules_per_day=1,
    include_weekends: bool = False,
):
    # Days generation
    days = []
    current_day = start_date
    while current_day <= end_date:
        if include_weekends or current_day.weekday() < 5:
            days.append(current_day)
        current_day += timedelta(days=1)

    # Time slots generation
    duration_delta = timedelta(hours=schedule_duration.hour, minutes=schedule_duration.minute)
    time_slots = []
    current_slot_start = datetime.combine(date.today(), schedule_start_time)
    end_limit = datetime.combine(date.today(), schedule_end_time)

    while current_slot_start + duration_delta <= end_limit:
        slot_start = current_slot_start.time()
        slot_end = (current_slot_start + duration_delta).time()
        time_slots.append((slot_start, slot_end))
        current_slot_start += duration_delta

    # Grouping existing schedules
    student_schedule_map = defaultdict(list)
    instructor_schedule_map = defaultdict(list)
    vehicle_schedule_map = defaultdict(list)

    for s in existing_group_schedules:
        instructor_schedule_map[s.instructor_id].append(s)

    practical_schedule_map = defaultdict(list)
    for p in existing_practice_schedules:
        student_schedule_map[p.student_id].append(p)
        practical_schedule_map[p.instructor_id].append(p)
        vehicle_schedule_map[p.vehicle_id].append(p)

    schedule_vars = {}
    prob = LpProblem("GroupScheduleGeneration", LpMaximize)

    for d in days:
        for start, end in time_slots:
            for vec in vehicle_ids:
                key = (student.id, d, start, vec)
                schedule_vars[key] = LpVariable(f"x_{student.id}_{d}_{start}_{vec}", cat=LpBinary)

    prob += lpSum(schedule_vars.values())

    # 1. Constraint schedules count per day
    for d in days:
        prob += (lpSum(schedule_vars[(student.id, d, start, vec)] for start, _ in time_slots
                for vec in vehicle_ids) <= schedules_per_day)

    # 2. Constraint total schedules count for student
    prob += lpSum(schedule_vars[(student.id, d, start, vec)] for d in days for start, _ in time_slots
                for vec in vehicle_ids) <= schedule_count

    # 3. Conflicts with existing schedules
    for d in days:
        for start, end in time_slots:
            for vec in vehicle_ids:
                key = (student.id, d, start, vec)

                # Student schedules conflict
                for p in student_schedule_map[student.id]:
                    if p.date == d and has_time_conflict(p.start_time, p.end_time, start, end):
                        prob += schedule_vars[key] == 0

                # Instructor schedules conflict
                for s in instructor_schedule_map[student.instructor_id]:
                    if s.date == d and has_time_conflict(s.start_time, s.end_time, start, end):
                        prob += schedule_vars[key] == 0

                # Vehicle schedules conflict
                for p in vehicle_schedule_map[vec]:
                    if p.date == d and has_time_conflict(p.start_time, p.end_time, start, end):
                        prob += schedule_vars[key] == 0

                # Instructor practice schedules conflict
                for p in practical_schedule_map[student.instructor_id]:
                    if p.date == d and has_time_conflict(p.start_time, p.end_time, start, end):
                        prob += schedule_vars[key] == 0

    # 4. Constraint student cannot be in multiple vehicles at the same time
    for d in days:
        for start, _ in time_slots:
            prob += lpSum(
                schedule_vars[(student.id, d, start, vec)]
                for vec in vehicle_ids
                if (student.id, d, start, vec) in schedule_vars
            ) <= 1

    prob.solve(PULP_CBC_CMD(msg=0))

    count = float(str(lpSum([v.value() for v in schedule_vars.values()])))

    if count < schedule_count:
        raise Exception(f'Not all schedules can be generated (only {count}/{schedule_count}), '
                        f'try wider date range or more schedules per day')

    result_list = []

    for (student_id, d, start, vec), var in schedule_vars.items():
        if var.value() == 1:
            end = (datetime.combine(d, start) + duration_delta).time()
            result_list.append(PracticeScheduleSchema(
                date=d, start_time=start, end_time=end, student_id=student_id,
                vehicle_id=vec, instructor_id=student.instructor_id
            ))

    return result_list
