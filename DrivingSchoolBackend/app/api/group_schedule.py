from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.exc import ProgrammingError

from core.models import db_helper
from core.schemas.group_schedule import GroupScheduleReadSchema, GroupScheduleCreateSchema, GroupScheduleUpdateSchema, \
    GroupScheduleButchCreateSchema
from crud import group_schedule as group_schedule_crud
from auth import user as auth_user

router = APIRouter(prefix="/group_schedules", tags=["Group Schedules"])


@router.post("/", response_model=GroupScheduleReadSchema)
async def create_schedule(
    data: GroupScheduleCreateSchema,
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await group_schedule_crud.create_group_schedule(session, data)
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.put("/{schedule_id}", response_model=GroupScheduleReadSchema)
async def update_schedule(
    schedule_id: int,
    data: GroupScheduleUpdateSchema,
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await group_schedule_crud.update_group_schedule(session, schedule_id, data)
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.get("/{schedule_id}", response_model=GroupScheduleReadSchema)
async def get_by_id(
    schedule_id: int,
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await group_schedule_crud.get_group_schedule_by_id(session, schedule_id)
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.get("/", response_model=list[GroupScheduleReadSchema])
async def get_all(
        payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await group_schedule_crud.get_all_group_schedules(session)
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.get("/groups/{group_id}", response_model=list[GroupScheduleReadSchema])
async def get_all_by_group_id(
    group_id: int,
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await group_schedule_crud.get_group_schedules_by_group_id(session, group_id)
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.post("/create_butch")
async def create_schedule_butch(
    data: GroupScheduleButchCreateSchema,
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await group_schedule_crud.create_butch_group_schedules(session, data)
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'{e}')
