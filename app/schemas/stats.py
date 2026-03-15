from pydantic import BaseModel


class UserStatsDTO(BaseModel):
    """Статистика пользователя для профиля."""

    total_tasks_solved: int
    """Количество уникальных задач, решённых студентом (записи в solutions)."""

    total_submissions: int
    """Общее количество попыток отправки кода (записи в submissions)."""

    topics_completed: int
    """Количество тем, полностью завершённых студентом."""

    success_rate: float
    """Процент попыток, завершившихся правильным ответом (0.0–100.0)."""
