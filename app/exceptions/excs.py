class AIStuding(Exception):
    detail = "Неожиданная ошибка"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


class ObjectNotFoundException(AIStuding):
    detail = "Объект не найден"


class ObjectAlreadyExistsException(AIStuding):
    detail = "Объект уже существует"


class EmptyUpdateDataException(AIStuding):
    detail = "Нет данных для обновления"
