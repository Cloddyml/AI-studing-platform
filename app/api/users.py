from fastapi import APIRouter, status

from app.api.deps.auth import UserIdDep
from app.api.deps.db import DBDep
from app.api.responses import generate_responses
from app.exceptions.excs import EmptyUpdateDataException, UserNotFoundException
from app.exceptions.http_excs import (
    EmptyUpdateDataHTTPException,
    UserNotFoundHTTPException,
)
from app.schemas.errors import StatusResponse
from app.schemas.users import UserPasswordOnlyDTO, UserUpdateRequestPatchDTO
from app.services.users import UsersService

router = APIRouter(prefix="/users", tags=["Пользователи"])


@router.patch(
    "/me",
    response_model=StatusResponse,
    status_code=status.HTTP_200_OK,
    responses=generate_responses(
        EmptyUpdateDataHTTPException,
        UserNotFoundHTTPException,
    ),
    summary="Частичное обновление профиля пользователя",
)
async def partial_update_user(
    db: DBDep, user_id: UserIdDep, user_data: UserUpdateRequestPatchDTO
):
    try:
        await UsersService(db).partial_update_user(user_id=user_id, user_data=user_data)
    except EmptyUpdateDataException:
        raise EmptyUpdateDataHTTPException
    except UserNotFoundException:
        raise UserNotFoundHTTPException
    return {"status": "OK"}


@router.patch(
    "/me/password",
    response_model=StatusResponse,
    status_code=status.HTTP_200_OK,
    responses=generate_responses(
        UserNotFoundHTTPException,
    ),
    summary="Обновление пароля пользователя",
)
async def update_user_password(
    db: DBDep, user_id: UserIdDep, user_password_data: UserPasswordOnlyDTO
):
    try:
        await UsersService(db).update_user_password(
            user_id=user_id,
            user_password_data=user_password_data,
        )
    except UserNotFoundException:
        raise UserNotFoundHTTPException
    return {"status": "OK"}
