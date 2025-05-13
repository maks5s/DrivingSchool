from fastapi import APIRouter, Depends

from core.models import db_helper
from core.schemas.user import UserReadSchema
from auth import user as auth_user
from crud import user as crud_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[UserReadSchema])
async def get_users(
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    async for session in db_helper.user_pwd_session_getter(username, password):
        users = await crud_user.get_all_users(session)

        return users
