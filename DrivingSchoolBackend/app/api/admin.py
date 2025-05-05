from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import ProgrammingError

from auth import user as auth_user
from core.models import db_helper
from crud.admin import get_admin_profile

router = APIRouter(prefix="/admins", tags=["Admin"])


@router.get("/{admin_id}/profile")
async def admin_profile(
    admin_id: int,
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            instructor = await get_admin_profile(session, admin_id)

            return instructor
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')
