from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import ProgrammingError

from core.models import db_helper
from core.schemas.vehicle import VehicleReadSchema, VehicleCreateSchema, VehicleUpdateSchema
from crud import vehicle as vehicle_crud
from auth import user as auth_user

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


@router.post("/", response_model=VehicleReadSchema)
async def create_vehicle(
    data: VehicleCreateSchema,
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await vehicle_crud.create_vehicle(session, data)
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.put("/{vehicle_id}", response_model=VehicleReadSchema)
async def update_vehicle(
    vehicle_id: int,
    data: VehicleUpdateSchema,
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await vehicle_crud.update_vehicle(session, vehicle_id, data)
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.get("/", response_model=list[VehicleReadSchema])
async def get_all_vehicles(
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await vehicle_crud.get_all_vehicles(session)
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.get("/{vehicle_id}", response_model=VehicleReadSchema)
async def get_vehicle_by_id(
    vehicle_id: int,
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await vehicle_crud.get_vehicle_by_id(session, vehicle_id)
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')
