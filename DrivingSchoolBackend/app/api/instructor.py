from fastapi import APIRouter, Depends, HTTPException, status

from core.models import db_helper
from core.schemas.category_level import CategoryLevelReadSchema
from core.schemas.instructor import InstructorReadSchema, InstructorCreateSchema, InstructorUpdateSchema
from crud import instructor as instructor_crud
from crud import instructor_category as instr_cat_crud
from sqlalchemy.exc import ProgrammingError
from auth import user as auth_user

router = APIRouter(prefix="/instructors", tags=["Instructor"])


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
