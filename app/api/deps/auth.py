from typing import Annotated

from fastapi import Depends, Request

from app.exceptions.excs import IncorrectTokenException
from app.exceptions.http_excs import (
    IncorrectTokenHTTPException,
    InsufficientPermissionsHTTPException,
    NoAccessTokenHTTPException,
    NoRefreshTokenHTTPException,
)
from app.services.auth import AuthService


def get_access_token(request: Request) -> str:
    token = request.cookies.get("access_token")
    if not token:
        raise NoAccessTokenHTTPException
    return token


def get_refresh_token(request: Request) -> str:
    token = request.cookies.get("refresh_token")
    if not token:
        raise NoRefreshTokenHTTPException
    return token


def get_current_user_id(access_token: str = Depends(get_access_token)) -> int:
    try:
        data = AuthService.decode_token(access_token)
    except IncorrectTokenException:
        raise IncorrectTokenHTTPException
    user_id = data.get("user_id")
    if user_id is None:
        raise IncorrectTokenHTTPException
    return user_id


def get_current_user_role(access_token: str = Depends(get_access_token)) -> str:
    try:
        data = AuthService.decode_token(access_token)
    except IncorrectTokenException:
        raise IncorrectTokenHTTPException
    role = data.get("role")
    if role is None:
        raise IncorrectTokenHTTPException
    return role


def require_admin(role: str = Depends(get_current_user_role)) -> None:
    if role != "admin":
        raise InsufficientPermissionsHTTPException


UserIdDep = Annotated[int, Depends(get_current_user_id)]
AdminDep = Annotated[None, Depends(require_admin)]
