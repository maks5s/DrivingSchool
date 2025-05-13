from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status, Query

from core.models import db_helper
from core.schemas.profile import StudentProfileSchema
from core.schemas.profile_schedule import StudentProfileScheduleSchema
from core.schemas.student import StudentReadSchema, StudentCreateSchema, StudentUpdateSchema, StudentPaginatedReadSchema
from crud import student as student_crud
from sqlalchemy.exc import ProgrammingError
from auth import user as auth_user
from crud.group_schedule import get_group_schedules_by_student_id_and_date
from crud.practice_schedule import get_practice_schedules_by_student_id_and_date
from crud.student import get_student_profile, get_students_paginated

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("/paginated", response_model=list[StudentPaginatedReadSchema])
async def get_paginated_students(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort_by: str = Query("last_name"),
    sort_order: Literal["asc", "desc"] = Query("asc"),
    category_level_id: int | None = Query(None),
    search: str | None = Query(None),
    only_without_sch: bool = Query(False),
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            students = await get_students_paginated(
                session=session,
                page=page,
                page_size=page_size,
                sort_by=sort_by,
                sort_order=sort_order,
                category_level_id=category_level_id,
                search=search,
                only_without_sch=only_without_sch,
            )

            return students
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.post("/", response_model=StudentReadSchema)
async def create_student(
    data: StudentCreateSchema,
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await student_crud.create_student(session, data)
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'{e}')


@router.put("/{student_id}", response_model=StudentReadSchema)
async def update_student(
    student_id: int,
    data: StudentUpdateSchema,
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await student_crud.update_student(session, student_id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'{e}')
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.get("/", response_model=list[StudentReadSchema])
async def get_all(
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await student_crud.get_all_students(session)
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.get("/{student_id}", response_model=StudentReadSchema)
async def get_by_id(
    student_id: int,
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await student_crud.get_student_by_id(session, student_id)
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.get("/{student_id}/schedule", response_model=list[StudentProfileScheduleSchema])
async def get_student_schedule(
    student_id: int,
    dt: date,
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            group_schedules = await get_group_schedules_by_student_id_and_date(session, student_id, dt)
            practice_schedules = await get_practice_schedules_by_student_id_and_date(session, student_id, dt)
            all_schedules = group_schedules + practice_schedules

            all_schedules.sort(key=lambda s: s.start_time)
            return all_schedules
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.get("/{student_id}/profile", response_model=StudentProfileSchema)
async def student_profile(
    student_id: int,
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            student = await get_student_profile(session, student_id)

            return student
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')
