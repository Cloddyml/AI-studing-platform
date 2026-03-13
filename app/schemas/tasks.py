from pydantic import BaseModel


class TaskBriefDTO(BaseModel):
    """Краткое представление задачи — для списка задач по теме."""

    id: int
    title: str
    description: str
    order_index: int
    time_limit_sec: int
    memory_limit_mb: int


class TaskDetailDTO(BaseModel):
    """Полное представление задачи — для страницы решения."""

    id: int
    topic_id: int
    title: str
    description: str
    starter_code: str | None
    order_index: int
    time_limit_sec: int
    memory_limit_mb: int
