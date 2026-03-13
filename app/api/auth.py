from fastapi import APIRouter, Request, Response, status

from app.api.deps.auth import AdminDep, get_refresh_token
from app.api.deps.db import DBDep
from app.api.responses import generate_responses
from app.core.config import settings
from app.exceptions.excs import (
    EmailNotRegisteredException,
    IncorrectPasswordException,
    IncorrectTokenException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from app.exceptions.http_excs import (
    AlreadyAuthenticatedHTTPException,
    AlreadyLoggedOutHTTPException,
    EmailNotRegisteredHTTPException,
    IncorrectPasswordHTTPException,
    IncorrectTokenHTTPException,
    InsufficientPermissionsHTTPException,
    UserAlreadyExistsHTTPException,
    UserNotFoundHTTPException,
)
from app.schemas.errors import StatusResponse
from app.schemas.users import UserLoginDTO, UserRequestAddDTO
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Авторизация и аутентификация"])


@router.post(
    "/register",
    response_model=StatusResponse,
    status_code=status.HTTP_201_CREATED,
    responses=generate_responses(UserAlreadyExistsHTTPException),
    summary="Регистрация пользователя",
)
async def register_user(
    db: DBDep,
    data: UserRequestAddDTO,
):
    try:
        await AuthService(db).register_user(data)
    except UserAlreadyExistsException:
        raise UserAlreadyExistsHTTPException

    return {"status": "OK"}


@router.post(
    "/login",
    response_model=StatusResponse,
    responses=generate_responses(
        AlreadyAuthenticatedHTTPException,
        EmailNotRegisteredHTTPException,
        IncorrectPasswordHTTPException,
    ),
    summary="Аутентификация пользователя",
)
async def login(
    request: Request,
    data: UserLoginDTO,
    response: Response,
    db: DBDep,
):
    raw_access = request.cookies.get("access_token")
    if raw_access:
        try:
            AuthService().decode_token(raw_access)
            raise AlreadyAuthenticatedHTTPException
        except IncorrectTokenException:
            pass

    try:
        access_token, refresh_token = await AuthService(db).login_user(data)
    except EmailNotRegisteredException:
        raise EmailNotRegisteredHTTPException
    except IncorrectPasswordException:
        raise IncorrectPasswordHTTPException

    response.set_cookie("access_token", access_token, httponly=True, samesite="lax")
    response.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=True,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )
    return {"status": "OK"}


@router.post(
    "/refresh",
    response_model=StatusResponse,
    responses=generate_responses(IncorrectTokenHTTPException),
    summary="Обновление access-токена",
)
async def refresh(
    request: Request,
    response: Response,
    db: DBDep,
):
    raw_refresh = get_refresh_token(request)
    try:
        new_access, new_refresh = await AuthService(db).refresh_access_token(
            raw_refresh
        )
    except IncorrectTokenException:
        raise IncorrectTokenHTTPException
    response.set_cookie("access_token", new_access, httponly=True, samesite="lax")
    response.set_cookie(
        "refresh_token",
        new_refresh,
        httponly=True,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )
    return {"status": "OK"}


@router.post(
    "/logout",
    response_model=StatusResponse,
    responses=generate_responses(AlreadyLoggedOutHTTPException),
    summary="Выход из аккаунта",
)
async def logout(
    request: Request,
    response: Response,
    db: DBDep,
):
    raw_refresh = request.cookies.get("refresh_token")

    if not raw_refresh:
        raise AlreadyLoggedOutHTTPException

    await AuthService(db).logout_user(raw_refresh)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"status": "OK"}


@router.delete(
    "/{user_id}",
    response_model=StatusResponse,
    responses=generate_responses(
        InsufficientPermissionsHTTPException,
        UserNotFoundHTTPException,
    ),
    summary="Удаление аккаунта пользователя",
    tags=["Для администраторов"],
)
async def delete_user(
    db: DBDep,
    user_id: int,
    _: AdminDep,
):
    try:
        await AuthService(db).delete_user(user_id=user_id)
    except UserNotFoundException:
        raise UserNotFoundHTTPException
    return {"status": "OK"}
