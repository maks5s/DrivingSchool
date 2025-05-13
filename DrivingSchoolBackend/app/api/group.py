from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status, Query

from core.models import db_helper
from core.schemas.group import GroupReadSchema, GroupCreateSchema, GroupUpdateSchema, GroupPaginatedReadSchema
from core.schemas.profile_schedule import ProfileScheduleSchema
from crud import group as group_crud
from sqlalchemy.exc import ProgrammingError
from auth import user as auth_user
from crud.group import get_groups_paginated
from crud.group_schedule import get_group_schedules_by_group_and_date

router = APIRouter(prefix="/groups", tags=["Groups"])


@router.get("/paginated", response_model=list[GroupPaginatedReadSchema])
async def get_paginated_groups(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    category_level_id: int | None = Query(None),
    search: str | None = Query(None),
    only_without_sch: bool = Query(False),
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            groups = await get_groups_paginated(
                session=session,
                page=page,
                page_size=page_size,
                category_level_id=category_level_id,
                search=search,
                only_without_sch=only_without_sch,
            )

            return groups
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.post("/", response_model=GroupReadSchema)
async def create_group_endpoint(
    data: GroupCreateSchema,
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await group_crud.create_group(session, data)
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.put("/{group_id}", response_model=GroupReadSchema)
async def update_group_endpoint(
    group_id: int,
    data: GroupUpdateSchema,
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await group_crud.update_group(session, group_id, data)
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.get("/", response_model=list[GroupReadSchema])
async def get_all_groups_endpoint(
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await group_crud.get_all_groups(session)
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.get("/{group_id}", response_model=GroupReadSchema)
async def get_group_by_id_endpoint(
    group_id: int,
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await group_crud.get_group_by_id(session, group_id)
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.get("/{group_id}/schedule", response_model=list[ProfileScheduleSchema])
async def get_group_schedule(
    group_id: int,
    dt: date,
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            group_schedules = await get_group_schedules_by_group_and_date(session, group_id, dt)

            return group_schedules
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')