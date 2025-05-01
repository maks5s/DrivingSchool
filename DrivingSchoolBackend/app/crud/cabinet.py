from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from core.models.cabinet import Cabinet
from core.schemas.cabinet import CabinetCreateSchema, CabinetUpdateSchema


async def create_cabinet(session: AsyncSession, data: CabinetCreateSchema):
    result = await session.execute(
        select(Cabinet)
        .where(Cabinet.name == data.name)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cabinet with this name already exists")

    cabinet = Cabinet(**data.model_dump())
    session.add(cabinet)
    await session.commit()
    await session.refresh(cabinet)
    return cabinet


async def update_cabinet(session: AsyncSession, cabinet_id: int, data: CabinetUpdateSchema):
    result = await session.execute(select(Cabinet).where(Cabinet.id == cabinet_id))
    cabinet = result.scalar_one_or_none()
    if not cabinet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cabinet not found")

    if cabinet.name != data.name:
        existing = await session.execute(
            select(Cabinet)
            .where(Cabinet.name == data.name)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Another cabinet with this name already exists"
            )

    cabinet.name = data.name
    await session.commit()
    await session.refresh(cabinet)
    return cabinet


async def get_all_cabinets(session: AsyncSession):
    result = await session.execute(select(Cabinet))
    return result.scalars().all()


async def get_cabinet_by_id(session: AsyncSession, cabinet_id: int):
    result = await session.execute(select(Cabinet).where(Cabinet.id == cabinet_id))
    cabinet = result.scalar_one_or_none()
    if not cabinet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cabinet not found")
    return cabinet
