from fastapi import APIRouter, status

from app.api.deps.auth import UserIdDep
from app.api.deps.db import DBDep
from app.api.responses import generate_responses
from app.exceptions.excs import (
    AIServiceException,
    TaskNotFoundException,
    TopicNotFoundException,
)
from app.exceptions.http_excs import (
    AIServiceHTTPException,
    TaskNotFoundHTTPException,
    TopicNotFoundHTTPException,
)
from app.schemas.ai_interactions import (
    AIResponseDTO,
    ExplainRequestDTO,
    HintRequestDTO,
)
from app.services.ai import AIService

router = APIRouter(prefix="/ai", tags=["AI-ассистент"])


@router.post(
    "/hint",
    response_model=AIResponseDTO,
    status_code=status.HTTP_200_OK,
    responses=generate_responses(TaskNotFoundHTTPException, AIServiceHTTPException),
    summary="Подсказка по задаче",
    description=(
        "Возвращает направляющую подсказку без готового решения. "
        "Принимает ID задачи и текущий код студента."
    ),
)
async def get_hint(
    db: DBDep,
    user_id: UserIdDep,
    data: HintRequestDTO,
) -> AIResponseDTO:
    try:
        return await AIService(db).get_hint(user_id=user_id, data=data)
    except TaskNotFoundException:
        raise TaskNotFoundHTTPException
    except AIServiceException:
        raise AIServiceHTTPException


@router.post(
    "/explain",
    response_model=AIResponseDTO,
    status_code=status.HTTP_200_OK,
    responses=generate_responses(TopicNotFoundHTTPException, AIServiceHTTPException),
    summary="Объяснение теории по теме",
    description=(
        "Отвечает на конкретный вопрос студента по теоретическому материалу темы. "
        "Принимает ID темы и вопрос."
    ),
)
async def explain_topic(
    db: DBDep,
    user_id: UserIdDep,
    data: ExplainRequestDTO,
) -> AIResponseDTO:
    try:
        return await AIService(db).explain_topic(user_id=user_id, data=data)
    except TopicNotFoundException:
        raise TopicNotFoundHTTPException
    except AIServiceException:
        raise AIServiceHTTPException
