class AIStuding(Exception):
    detail = "Неожиданная ошибка"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


class ObjectNotFoundException(AIStuding):
    detail = "Объект не найден"


class UserNotFoundException(ObjectNotFoundException):
    detail = "Пользователь не найден"


class ObjectAlreadyExistsException(AIStuding):
    detail = "Объект уже существует"


class EmptyUpdateDataException(AIStuding):
    detail = "Нет данных для обновления"


class UserAlreadyExistsException(AIStuding):
    detail = "Пользователь с таким email или именем уже существует"


class AlreadyAuthenticatedException(AIStuding):
    detail = "Пользователь уже авторизован"


class AlreadyLoggedOutException(Exception):
    detail = "Пользователь уже вышел"


class EmailNotRegisteredException(AIStuding):
    detail = "Пользователь с таким email не зарегистрирован"


class IncorrectPasswordException(AIStuding):
    detail = "Неверный пароль"


class IncorrectTokenException(AIStuding):
    detail = "Токен недействителен или истёк"


class TokenRevokedException(AIStuding):
    detail = "Токен был отозван"
