from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Vehicle
from core.schemas.vehicle import VehicleCreateSchema, VehicleUpdateSchema


async def create_vehicle(session: AsyncSession, data: VehicleCreateSchema):
    result = await session.execute(
        select(Vehicle)
        .where(Vehicle.license_plate == data.license_plate)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vehicle with this license plate already exists"
        )

    vehicle = Vehicle(**data.model_dump())
    session.add(vehicle)
    await session.commit()
    await session.refresh(vehicle)
    return vehicle


async def update_vehicle(session: AsyncSession, vehicle_id: int, data: VehicleUpdateSchema):
    result = await session.execute(
        select(Vehicle)
        .where(Vehicle.id == vehicle_id)
    )
    vehicle = result.scalar_one_or_none()
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")

    if vehicle.license_plate != data.license_plate:
        existing = await session.execute(
            select(Vehicle)
            .where(Vehicle.license_plate == data.license_plate)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Another vehicle with this license plate already exists"
            )

    for field, value in data.model_dump().items():
        setattr(vehicle, field, value)

    await session.commit()
    await session.refresh(vehicle)
    return vehicle


async def get_all_vehicles(session: AsyncSession):
    result = await session.execute(select(Vehicle))
    return result.scalars().all()


async def get_all_vehicles_by_category_level(session: AsyncSession, category_level_id: int):
    result = await session.execute(select(Vehicle).where(Vehicle.category_level_id == category_level_id))
    return result.scalars().all()


async def get_vehicle_by_id(session: AsyncSession, vehicle_id: int):
    result = await session.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    vehicle = result.scalar_one_or_none()
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
    return vehicle
