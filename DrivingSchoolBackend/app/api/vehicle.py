from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.exc import ProgrammingError

from core.models import db_helper
from core.schemas.vehicle import VehicleReadSchema, VehicleCreateSchema, VehicleUpdateSchema
from crud import vehicle as vehicle_crud
from auth import user as auth_user
from crud.vehicle import get_vehicles_paginated

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


@router.get("/paginated", response_model=list[VehicleReadSchema])
async def get_paginated_vehicles(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    category_level_id: int | None = Query(None),
    search: str | None = Query(None),
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            vehicles = await get_vehicles_paginated(
                session=session,
                page=page,
                page_size=page_size,
                category_level_id=category_level_id,
                search=search,
            )

            return vehicles
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


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
