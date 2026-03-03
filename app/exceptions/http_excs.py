from fastapi import HTTPException, status


class AIStudingHTTPException(HTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Внутренняя ошибка сервера"

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class ObjectNotFoundHTTPException(AIStudingHTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Объект не найден"


class UserNotFoundHTTPException(ObjectNotFoundHTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Пользователь не найден"


class ObjectAlreadyExistsHTTPException(AIStudingHTTPException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Объект уже существует"


class UserAlreadyExistsHTTPException(ObjectAlreadyExistsHTTPException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Пользователь с таким email или именем уже существует"


class AlreadyAuthenticatedHTTPException(AIStudingHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Вы уже авторизованы"


class AlreadyLoggedOutHTTPException(AIStudingHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Вы уже вышли из системы"


class NoAccessTokenHTTPException(AIStudingHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Отсутствует токен доступа"


class NoRefreshTokenHTTPException(AIStudingHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Отсутствует refresh-токен"


class IncorrectTokenHTTPException(AIStudingHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Токен недействителен или истёк"


class EmailNotRegisteredHTTPException(AIStudingHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверный email или пароль"


class IncorrectPasswordHTTPException(AIStudingHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверный email или пароль"
