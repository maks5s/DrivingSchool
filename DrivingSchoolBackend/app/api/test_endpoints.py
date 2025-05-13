from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models import db_helper
from auth import user as auth_user
from crud import user as crud_user
from core.schemas.user import UserWithRoleReadSchema


router = APIRouter(prefix="/tests", tags=["TestEndpoints"])


@router.get("/")
async def root(session: AsyncSession = Depends(db_helper.session_getter)):
    try:
        res = await session.execute(text("""
        SELECT username FROM "user";
"""))
        # await session.commit()
        return res.scalars().all()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


async def get_current_auth_user(
    payload: dict = Depends(auth_user.get_current_token_payload)
) -> UserWithRoleReadSchema:
    user_id = int(payload.get("sub"))
    username = payload.get("username")
    password = payload.get("password")
    role = payload.get("role")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            user = await crud_user.get_user_by_id(session, user_id)

            return UserWithRoleReadSchema(
                id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                patronymic=user.patronymic,
                birthday=user.birthday,
                phone_number=user.phone_number,
                role=role,
            )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


async def get_current_admin_auth_user(
    user: UserWithRoleReadSchema = Depends(get_current_auth_user)
):
    if user.role == settings.roles.admin:
        return user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.get("/info_admin")
async def info(
    user: UserWithRoleReadSchema = Depends(get_current_admin_auth_user)
):
    return user
