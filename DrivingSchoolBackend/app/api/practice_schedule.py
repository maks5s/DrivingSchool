from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.exc import ProgrammingError

from core.models import db_helper
from core.schemas.practice_schedule import PracticeScheduleReadSchema, PracticeScheduleCreateSchema, \
    PracticeScheduleUpdateSchema, PracticeScheduleButchCreateSchema
from crud import practice_schedule as practice_schedule_crud
from auth import user as auth_user

router = APIRouter(prefix="/practice_schedules", tags=["Practice Schedules"])


@router.post("/", response_model=PracticeScheduleReadSchema)
async def create_schedule(
    data: PracticeScheduleCreateSchema,
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await practice_schedule_crud.create_practice_schedule(session, data)
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.put("/{schedule_id}", response_model=PracticeScheduleReadSchema)
async def update_schedule(
    schedule_id: int,
    data: PracticeScheduleUpdateSchema,
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await practice_schedule_crud.update_practice_schedule(session, schedule_id, data)
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.get("/{schedule_id}", response_model=PracticeScheduleReadSchema)
async def get_by_id(
    schedule_id: int,
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await practice_schedule_crud.get_practice_schedule_by_id(session, schedule_id)
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.get("/", response_model=list[PracticeScheduleReadSchema])
async def get_all(
        payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await practice_schedule_crud.get_all_practice_schedules(session)
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.get("/students/{student_id}", response_model=list[PracticeScheduleReadSchema])
async def get_all_by_student_id(
    student_id: int,
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await practice_schedule_crud.get_all_practice_schedules_by_student_id(session, student_id)
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.post("/create_butch")
async def create_schedule_butch(
    data: PracticeScheduleButchCreateSchema,
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await practice_schedule_crud.create_butch_practice_schedules(session, data)
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'{e}')
