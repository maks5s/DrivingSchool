from fastapi import APIRouter, Depends, HTTPException, status

from core.models import db_helper
from core.schemas.category_level import CategoryLevelReadSchema, CategoryLevelCreateSchema, CategoryLevelUpdateSchema
from crud import category_level as crud
from sqlalchemy.exc import ProgrammingError
from auth import user as auth_user

router = APIRouter(prefix="/category_levels", tags=["CategoryLevels"])


@router.post("/", response_model=CategoryLevelReadSchema)
async def create(
    data: CategoryLevelCreateSchema,
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await crud.create_category_level(session, data)
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.put("/{category_level_id}", response_model=CategoryLevelReadSchema)
async def update(
    category_level_id: int,
    data: CategoryLevelUpdateSchema,
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await crud.update_category_level(session, category_level_id, data)
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.get("/", response_model=list[CategoryLevelReadSchema])
async def get_all(
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await crud.get_all_category_levels(session)
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.get("/{category_level_id}", response_model=CategoryLevelReadSchema)
async def get_by_id(
    category_level_id: int,
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await crud.get_category_level_by_id(session, category_level_id)
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')
