from datetime import datetime

from pydantic import BaseModel


class SubmissionDTO(BaseModel):
    id: int
    user_id: int
    task_id: int
    code: str
    status: str
    stdout: str | None
    stderr: str | None
    is_tests_passed: bool | None
    created_at: datetime


class SubmissionAddDTO(BaseModel):
    user_id: int
    task_id: int
    code: str
