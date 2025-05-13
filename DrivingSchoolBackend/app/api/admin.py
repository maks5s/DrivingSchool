import json
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.exc import ProgrammingError

from auth import user as auth_user
from core.models import db_helper
from core.schemas.admin import AdminUpdateSchema
from core.schemas.profile import AdminProfileSchema
from core.schemas.user import UserReadSchema
from crud import admin as crud_admin
from crud.data_management import load_initial_data, generate_test_data, get_export_data

router = APIRouter(prefix="/admins", tags=["Admin"])


@router.post("/load_data")
async def load_seed_data(
    file: UploadFile,
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            contents = await file.read()
            data = json.loads(contents)
            return await load_initial_data(data, session)
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.post("/generate_data")
async def generate_data_test(
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await generate_test_data(session)
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.get("/export_groups", response_class=FileResponse)
async def export_groups(
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            data = await get_export_data(session)

            with NamedTemporaryFile(delete=False, mode='w', suffix=".json", encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                temp_file_path = f.name

            return FileResponse(
                path=temp_file_path,
                filename="groups_export.json",
                media_type="application/json",
                headers={"Content-Disposition": "attachment; filename=groups_export.json"}
            )
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.get("/{admin_id}/profile", response_model=AdminProfileSchema)
async def admin_profile(
    admin_id: int,
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            instructor = await crud_admin.get_admin_profile(session, admin_id)

            return instructor
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')


@router.put("/{admin_id}", response_model=UserReadSchema)
async def update_admin(
    admin_id: int,
    data: AdminUpdateSchema,
    payload: dict = Depends(auth_user.get_current_token_payload)
):
    username = payload.get("username")
    password = payload.get("password")

    try:
        async for session in db_helper.user_pwd_session_getter(username, password):
            return await crud_admin.update_admin(session, admin_id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'{e}')
    except ProgrammingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have no permissions')
