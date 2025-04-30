from asyncpg import ConnectionDoesNotExistError
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import InvalidTokenError

from core.models import db_helper
from core.schemas.user import UserJWTSchema
from crud import user as crud_user
from auth import utils as auth_utils

http_bearer = HTTPBearer()


async def validate_auth_user(
    username: str,
    password: str,
):
    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            user = await crud_user.get_user_by_username(session, username)
            user_role = await crud_user.get_user_role_by_username(session, username)

            return UserJWTSchema(
                id=user.id,
                username=username,
                password=password,
                role=user_role,
            )
    except ConnectionDoesNotExistError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid username or password")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


async def get_current_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer)
):
    token = credentials.credentials
    try:
        payload = auth_utils.decode_jwt(token)
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')

    return payload
