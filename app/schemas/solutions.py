from datetime import datetime

from pydantic import BaseModel


class SolutionDTO(BaseModel):
    id: int
    user_id: int
    task_id: int
    code: str
    is_tests_passed: bool
    solved_at: datetime


class SolutionAddDTO(BaseModel):
    """Используется Celery-воркером для записи финального решения."""

    user_id: int
    task_id: int
    code: str
    # is_tests_passed всегда True при записи в solutions (только ACCEPTED попадает сюда)
    is_tests_passed: bool = True
