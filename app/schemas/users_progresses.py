from datetime import datetime

from pydantic import BaseModel


class UserProgressDTO(BaseModel):
    id: int
    user_id: int
    topic_id: int
    tasks_total: int
    tasks_solved: int
    is_completed: bool
    completed_at: datetime | None
