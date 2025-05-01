from fastapi import APIRouter

from core.schemas.login import LoginSchema
from core.schemas.token import TokenInfo
from auth import user as auth_user
from auth import utils as auth_utils

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenInfo)
async def auth_user_issue_jwt(
    login_data: LoginSchema,
):
    user = await auth_user.validate_auth_user(login_data.username, login_data.password)
    jwt_payload = {
        "sub": str(user.id),
        "username": user.username,
        "password": user.password,
        "role": user.role,
    }
    token = auth_utils.encode_jwt(jwt_payload)
    return TokenInfo(
        access_token=token,
        token_type="Bearer",
    )
