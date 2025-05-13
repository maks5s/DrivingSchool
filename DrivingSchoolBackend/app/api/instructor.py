from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import ValidationError

from core.models import db_helper
from core.schemas.category_level import CategoryLevelReadSchema
from core.schemas.instructor import InstructorReadSchema, InstructorCreateSchema, InstructorUpdateSchema
from core.schemas.profile import InstructorProfileSchema
from core.schemas.profile_schedule import InstructorProfileScheduleSchema
from crud import instructor as instructor_crud
from crud import instructor_category as instr_cat_crud
from sqlalchemy.exc import ProgrammingError
from auth import user as auth_user
from crud.group_schedule import get_group_schedules_by_instructor_and_date
from crud.instructor import get_instructor_profile, get_instructors_paginated
from crud.practice_schedule import get_practice_schedules_by_instructor_and_date

router = APIRouter(prefix="/instructors", tags=["Instructors"])


@router.get("/paginated", response_model=list[InstructorReadSchema])
async def get_paginated_instructors(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort_by: str = Query("last_name"),
    sort_order: Literal["asc", "desc"] = Query("asc"),
    category_level_id: int | None = Query(None),
    search: str | None = Query(None),
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            instructors = await get_instructors_paginated(
                session=session,
                page=page,
                page_size=page_size,
                sort_by=sort_by,
                sort_order=sort_order,
                category_level_id=category_level_id,
                search=search,
            )

            return instructors
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.post("/", response_model=InstructorReadSchema)
async def create_instructor(
    data: InstructorCreateSchema,
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await instructor_crud.create_instructor(session, data)
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'{e.errors()[0]['loc']}: {e.errors()[0]['msg']}')
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'{e}')


@router.put("/{instructor_id}", response_model=InstructorReadSchema)
async def update_instructor(
    instructor_id: int,
    data: InstructorUpdateSchema,
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await instructor_crud.update_instructor(session, instructor_id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'{e}')
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.get("/", response_model=list[InstructorReadSchema])
async def get_all(
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await instructor_crud.get_all_instructors(session)
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.get("/{instructor_id}", response_model=InstructorReadSchema)
async def get_by_id(
    instructor_id: int,
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await instructor_crud.get_instructor_by_id(session, instructor_id)
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.post("/{instructor_id}/categories")
async def add_category(
    instructor_id: int,
    category_level_id: int,
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await instr_cat_crud.add_category_to_instructor(session, instructor_id, category_level_id)
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.delete("/{instructor_id}/categories/{category_level_id}")
async def remove_category(
    instructor_id: int,
    category_level_id: int,
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await instr_cat_crud.remove_category_from_instructor(session, instructor_id, category_level_id)
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.get("/{instructor_id}/categories", response_model=list[CategoryLevelReadSchema])
async def get_categories(
    instructor_id: int,
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await instr_cat_crud.get_instructor_categories(session, instructor_id)
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.get("/{instructor_id}/schedule", response_model=list[InstructorProfileScheduleSchema])
async def get_instructor_schedule(
    instructor_id: int,
    dt: date,
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            group_schedules = await get_group_schedules_by_instructor_and_date(session, instructor_id, dt)
            practice_schedules = await get_practice_schedules_by_instructor_and_date(session, instructor_id, dt)
            schedules = group_schedules + practice_schedules

            schedules.sort(key=lambda x: x.start_time)
            return schedules
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.get("/{instructor_id}/profile", response_model=InstructorProfileSchema)
async def instructor_profile(
    instructor_id: int,
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            instructor = await get_instructor_profile(session, instructor_id)

            return instructor
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')
