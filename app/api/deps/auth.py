from typing import Annotated

from fastapi import Depends, Request

from app.exceptions.excs import IncorrectTokenException
from app.exceptions.http_excs import (
    IncorrectTokenHTTPException,
    NoAccessTokenHTTPException,
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
        raise NoAccessTokenHTTPException
    return token


def get_current_user_id(access_token: str = Depends(get_access_token)) -> int:
    try:
        data = AuthService().decode_token(access_token)
    except IncorrectTokenException:
        raise IncorrectTokenHTTPException
    return data["user_id"]


UserIdDep = Annotated[int, Depends(get_current_user_id)]
