from datetime import date, timedelta, time, datetime
from pulp import LpProblem, LpVariable, LpBinary, lpSum, LpMaximize, PULP_CBC_CMD
from typing import List
from collections import defaultdict

from core.schemas.group_schedule import GroupScheduleSchema, GroupForScheduleSchema, ExistingGroupScheduleSchema
from core.schemas.practice_schedule import ExistingPracticeScheduleSchema


def has_time_conflict(start1, end1, start2, end2):
    return start1 < end2 and start2 < end1


def generate_group_schedule(
    group: GroupForScheduleSchema,
    cabinet_ids: List[int],
    existing_group_schedules: List[ExistingGroupScheduleSchema],
    existing_practice_schedules: List[ExistingPracticeScheduleSchema],
    start_date: date = date.today() + timedelta(days=1),
    end_date: date = date.today() + timedelta(days=30),
    schedule_start_time: time = time(8, 0),
    schedule_end_time: time = time(18, 0),
    schedule_duration: time = time(2, 0),
    schedule_count=60,
    schedules_per_day=3,
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
    group_schedule_map = defaultdict(list)
    instructor_schedule_map = defaultdict(list)
    cabinet_schedule_map = defaultdict(list)

    for s in existing_group_schedules:
        group_schedule_map[s.group_id].append(s)
        instructor_schedule_map[s.instructor_id].append(s)
        cabinet_schedule_map[s.cabinet_id].append(s)

    practical_schedule_map = defaultdict(list)
    for p in existing_practice_schedules:
        practical_schedule_map[p.instructor_id].append(p)

    schedule_vars = {}
    prob = LpProblem("GroupScheduleGeneration", LpMaximize)

    for d in days:
        for start, end in time_slots:
            for cab in cabinet_ids:
                key = (group.id, d, start, cab)
                schedule_vars[key] = LpVariable(f"x_{group.id}_{d}_{start}_{cab}", cat=LpBinary)

    prob += lpSum(schedule_vars.values())

    # 1. Constraint schedules count per day
    for d in days:
        prob += lpSum(schedule_vars[(group.id, d, start, cab)] for start, _ in time_slots
                      for cab in cabinet_ids) <= schedules_per_day

    # 2. Constraint total schedules count for group
    prob += lpSum(schedule_vars[(group.id, d, start, cab)] for d in days for start, _ in time_slots
                  for cab in cabinet_ids) <= schedule_count

    # 3. Conflicts with existing schedules
    for d in days:
        for start, end in time_slots:
            for cab in cabinet_ids:
                key = (group.id, d, start, cab)

                # Group schedules conflict
                for s in group_schedule_map[group.id]:
                    if s.date == d and has_time_conflict(s.start_time, s.end_time, start, end):
                        prob += schedule_vars[key] == 0

                # Instructor schedules conflict
                for s in instructor_schedule_map[group.instructor_id]:
                    if s.date == d and has_time_conflict(s.start_time, s.end_time, start, end):
                        prob += schedule_vars[key] == 0

                # Cabinets schedules conflict
                for s in cabinet_schedule_map[cab]:
                    if s.date == d and has_time_conflict(s.start_time, s.end_time, start, end):
                        prob += schedule_vars[key] == 0

                # Instructor practice schedules conflict
                for p in practical_schedule_map[group.instructor_id]:
                    if p.date == d and has_time_conflict(p.start_time, p.end_time, start, end):
                        prob += schedule_vars[key] == 0

    # 4. Constraint group cannot be in multiple cabinets at the same time
    for d in days:
        for start, _ in time_slots:
            prob += lpSum(
                schedule_vars[(group.id, d, start, cab)]
                for cab in cabinet_ids
                if (group.id, d, start, cab) in schedule_vars
            ) <= 1

    prob.solve(PULP_CBC_CMD(msg=0))

    count = float(str(lpSum([v.value() for v in schedule_vars.values()])))

    if count < schedule_count:
        raise Exception(f'Not all schedules are generated (only {count}), try wider date range')

    result_list = []

    for (group_id, d, start, cab), var in schedule_vars.items():
        if var.value() == 1:
            end = (datetime.combine(d, start) + duration_delta).time()
            result_list.append(GroupScheduleSchema(
                date=d, start_time=start, end_time=end, group_id=group_id, cabinet_id=cab
            ))

    return result_list
