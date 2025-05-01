from fastapi import APIRouter, Depends, HTTPException, status

from core.models import db_helper
from core.schemas.group import GroupReadSchema, GroupCreateSchema, GroupUpdateSchema
from crud import group as group_crud
from sqlalchemy.exc import ProgrammingError
from auth import user as auth_user

router = APIRouter(prefix="/groups", tags=["Groups"])


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
