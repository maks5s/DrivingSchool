from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import ProgrammingError

from core.models import db_helper
from core.schemas.cabinet import CabinetReadSchema, CabinetCreateSchema, CabinetUpdateSchema
from crud import cabinet as cabinet_crud
from auth import user as auth_user

router = APIRouter(prefix="/cabinets", tags=["Cabinets"])


@router.post("/", response_model=CabinetReadSchema)
async def create_cabinet(
    data: CabinetCreateSchema,
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await cabinet_crud.create_cabinet(session, data)
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.put("/{cabinet_id}", response_model=CabinetReadSchema)
async def update_cabinet(
    cabinet_id: int,
    data: CabinetUpdateSchema,
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await cabinet_crud.update_cabinet(session, cabinet_id, data)
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.get("/", response_model=list[CabinetReadSchema])
async def get_all_cabinets(
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await cabinet_crud.get_all_cabinets(session)
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.get("/{cabinet_id}", response_model=CabinetReadSchema)
async def get_cabinet_by_id(
    cabinet_id: int,
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await cabinet_crud.get_cabinet_by_id(session, cabinet_id)
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')
