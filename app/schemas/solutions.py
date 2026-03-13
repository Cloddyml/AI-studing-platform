from datetime import datetime

from pydantic import BaseModel


class SolutionDTO(BaseModel):
    id: int
    task_id: int
    code: str
    is_tests_passed: bool
    solved_at: datetime
