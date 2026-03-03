from fastapi import APIRouter, Request, Response

from app.api.deps.auth import get_refresh_token
from app.api.deps.db import DBDep
from app.core.config import settings
from app.exceptions.excs import UserAlreadyExistsException, UserNotFoundException
from app.exceptions.http_excs import (
    UserAlreadyExistsHTTPException,
    UserNotFoundHTTPException,
)
from app.schemas.users import UserRequestAddDTO
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Авторизация и аутентификация"])


@router.post("/register")
async def register_user(
    db: DBDep,
    data: UserRequestAddDTO,
):
    try:
        await AuthService(db).register_user(data)
    except UserAlreadyExistsException:
        raise UserAlreadyExistsHTTPException

    return {"status": "OK"}


@router.post("/login")
async def login(
    data: UserRequestAddDTO,
    response: Response,
    db: DBDep,
):
    access_token, refresh_token = await AuthService(db).login_user(data)
    response.set_cookie("access_token", access_token, httponly=True, samesite="lax")
    response.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=True,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )
    return {"status": "OK"}


@router.post("/refresh")
async def refresh(
    request: Request,
    response: Response,
    db: DBDep,
):
    raw_refresh = get_refresh_token(request)
    new_access, new_refresh = await AuthService(db).refresh_access_token(raw_refresh)
    response.set_cookie("access_token", new_access, httponly=True, samesite="lax")
    response.set_cookie(
        "refresh_token",
        new_refresh,
        httponly=True,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )
    return {"status": "OK"}


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    db: DBDep,
):
    raw_refresh = request.cookies.get("refresh_token")
    if raw_refresh:
        await AuthService(db).logout_user(raw_refresh)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"status": "OK"}


@router.delete("/{user_id}", summary="Удаление аккаунта пользователя")
async def delete_user(
    db: DBDep,
    user_id: int,
):
    try:
        await AuthService(db).delete_user(user_id=user_id)
    except UserNotFoundException:
        raise UserNotFoundHTTPException
    return {"status": "OK"}
