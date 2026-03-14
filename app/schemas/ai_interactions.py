import enum
from datetime import datetime

from pydantic import BaseModel, Field


class InteractionType(str, enum.Enum):
    HINT = "hint"
    EXPLAIN = "explain"


class AIInteractionAddDTO(BaseModel):
    user_id: int
    task_id: int | None
    topic_id: int | None
    interaction_type: str
    user_message: str | None
    ai_response: str | None
    response_time_ms: int | None


class AIInteractionDTO(BaseModel):
    id: int
    user_id: int
    task_id: int | None
    topic_id: int | None
    interaction_type: str
    user_message: str | None
    ai_response: str | None
    response_time_ms: int | None
    created_at: datetime


class HintRequestDTO(BaseModel):
    task_id: int
    user_code: str = Field(min_length=1)


class ExplainRequestDTO(BaseModel):
    topic_id: int
    question: str = Field(
        min_length=5,
        max_length=1000,
        description="Конкретный вопрос студента по теории темы",
    )


class AIResponseDTO(BaseModel):
    response: str
    response_time_ms: int
