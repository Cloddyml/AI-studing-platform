from datetime import datetime

from pydantic import BaseModel, Field

from app.models.submissions import SubmissionStatus


class SubmissionDTO(BaseModel):
    """Ответ на GET /submissions/{id} — используется для поллинга статуса."""

    id: int
    user_id: int
    task_id: int
    status: SubmissionStatus
    stdout: str | None
    stderr: str | None
    is_tests_passed: bool | None
    created_at: datetime
    updated_at: datetime


class SubmissionAddDTO(BaseModel):
    """Создание новой записи submission. Используется сервисом при POST /tasks/{id}/submit."""

    user_id: int
    task_id: int
    code: str


class SubmitRequestDTO(BaseModel):
    """Тело запроса POST /tasks/{id}/submit."""

    code: str = Field(..., min_length=1, max_length=50_000, description="Код студента")


class SubmitResponseDTO(BaseModel):
    """Ответ на POST /tasks/{id}/submit — возвращает ID для поллинга."""

    submission_id: int
    status: SubmissionStatus
