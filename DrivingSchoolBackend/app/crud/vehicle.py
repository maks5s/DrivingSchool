from fastapi import HTTPException, status
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Vehicle
from core.schemas.vehicle import VehicleCreateSchema, VehicleUpdateSchema
from crud.category_level import get_category_level_by_id


async def create_vehicle(session: AsyncSession, data: VehicleCreateSchema):
    existing = await get_category_level_by_id(session, data.category_level_id)

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
    existing = await get_category_level_by_id(session, data.category_level_id)

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


async def get_vehicles_paginated(
    session: AsyncSession,
    page: int = 1,
    page_size: int = 10,
    category_level_id: int | None = None,
    search: str | None = None
):
    if category_level_id:
        existing = await get_category_level_by_id(session, category_level_id)

    stmt = (
        select(Vehicle)
        .order_by(Vehicle.brand, Vehicle.model)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    if category_level_id:
        stmt = stmt.where(
            Vehicle.category_level_id == category_level_id
        )

    if search:
        stmt = stmt.filter(
            or_(
                Vehicle.brand.ilike(f"%{search}%"),
                Vehicle.model.ilike(f"%{search}%"),
                Vehicle.license_plate.ilike(f"%{search}%"),
            )
        )

    result = await session.execute(stmt)
    return result.scalars().all()
