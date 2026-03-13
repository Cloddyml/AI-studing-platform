class AIStuding(Exception):
    detail = "Неожиданная ошибка"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


class ObjectNotFoundException(AIStuding):
    detail = "Объект не найден"


class UserNotFoundException(ObjectNotFoundException):
    detail = "Пользователь не найден"


class TopicNotFoundException(ObjectNotFoundException):
    detail = "Тема не найдена"


class TaskNotFoundException(ObjectNotFoundException):
    detail = "Задача не найдена"


class SolutionNotFoundException(ObjectNotFoundException):
    detail = "Решение не найдено"


class ObjectAlreadyExistsException(AIStuding):
    detail = "Объект уже существует"


class UserAlreadyExistsException(ObjectAlreadyExistsException):
    detail = "Пользователь с таким email или именем уже существует"


class EmptyUpdateDataException(AIStuding):
    detail = "Нет данных для обновления"


class EmailNotRegisteredException(AIStuding):
    detail = "Пользователь с таким email не зарегистрирован"


class IncorrectPasswordException(AIStuding):
    detail = "Неверный пароль"


class IncorrectTokenException(AIStuding):
    detail = "Токен недействителен или истёк"
