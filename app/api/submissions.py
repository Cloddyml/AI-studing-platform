from fastapi import APIRouter, status

from app.api.deps.auth import UserIdDep
from app.api.deps.db import DBDep
from app.api.responses import generate_responses
from app.exceptions.excs import SubmissionNotFoundException
from app.exceptions.http_excs import SubmissionNotFoundHTTPException
from app.schemas.submissions import SubmissionDTO
from app.services.submissions import SubmissionsService

router = APIRouter(prefix="/submissions", tags=["Попытки выполнения"])


@router.get(
    "/{submission_id}",
    response_model=SubmissionDTO,
    status_code=status.HTTP_200_OK,
    responses=generate_responses(SubmissionNotFoundHTTPException),
    summary="Получение статуса попытки выполнения кода",
    description=(
        "Используется для поллинга после POST /tasks/{id}/submit. "
        "Пока статус `pending` или `running` — повторяйте запрос. "
        "Финальные статусы: `accepted`, `wrong_answer`, `time_limit`, "
        "`memory_limit`, `runtime_error`, `internal_error`."
    ),
)
async def get_submission(
    db: DBDep,
    user_id: UserIdDep,
    submission_id: int,
):
    try:
        return await SubmissionsService(db).get_submission(
            submission_id=submission_id,
            user_id=user_id,
        )
    except SubmissionNotFoundException:
        raise SubmissionNotFoundHTTPException
