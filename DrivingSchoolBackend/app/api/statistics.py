from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import ProgrammingError

from core.models import db_helper
from core.schemas.statistics import StatisticsResponseSchema
from auth import user as auth_user
from crud.statistics import get_statistics

router = APIRouter(prefix="/statistics", tags=["Statistics"])


@router.get("/", response_model=StatisticsResponseSchema)
async def statistics(
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await get_statistics(session)
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')
