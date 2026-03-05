from fastapi import APIRouter, status

from app.api.deps.auth import UserIdDep
from app.api.deps.db import DBDep
from app.schemas.errors import StatusResponse
from app.schemas.users import UserPasswordOnlyDTO, UserUpdateRequestDTO
from app.services.users import UsersService

router = APIRouter(prefix="/users", tags=["Пользователи"])


@router.patch(
    "/partial_update_user",
    response_model=StatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Частичное обновление профиля пользователя",
)
async def partial_update_user(
    db: DBDep, user_id: UserIdDep, user_data: UserUpdateRequestDTO
):
    await UsersService(db).partial_update_user(user_id=user_id, user_data=user_data)
    return {"status": "OK"}


@router.patch(
    "/update_user_password",
    response_model=StatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновление пароля пользователя",
)
async def update_user_password(
    db: DBDep, user_id: UserIdDep, user_password_data: UserPasswordOnlyDTO
):
    await UsersService(db).update_user_password(
        user_id=user_id,
        user_password_data=user_password_data,
    )
    return {"status": "OK"}
