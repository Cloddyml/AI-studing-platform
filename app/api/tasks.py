from fastapi import APIRouter, status

from app.api.deps.auth import UserIdDep
from app.api.deps.db import DBDep
from app.api.responses import generate_responses
from app.exceptions.excs import SolutionNotFoundException, TaskNotFoundException
from app.exceptions.http_excs import (
    SolutionNotFoundHTTPException,
    SubmissionNotFoundHTTPException,
    TaskNotFoundHTTPException,
)
from app.schemas.solutions import SolutionDTO
from app.schemas.submissions import SubmitRequestDTO, SubmitResponseDTO
from app.schemas.tasks import TaskDetailDTO
from app.services.submissions import SubmissionsService
from app.services.tasks import TasksService

router = APIRouter(prefix="/tasks", tags=["Задачи"])


@router.get(
    "/{task_id}",
    response_model=TaskDetailDTO,
    status_code=status.HTTP_200_OK,
    responses=generate_responses(TaskNotFoundHTTPException),
    summary="Получение условия задачи",
)
async def get_task(db: DBDep, _: UserIdDep, task_id: int):
    try:
        return await TasksService(db).get_task_by_id(task_id)
    except TaskNotFoundException:
        raise TaskNotFoundHTTPException


@router.post(
    "/{task_id}/submit",
    response_model=SubmitResponseDTO,
    status_code=status.HTTP_202_ACCEPTED,
    responses=generate_responses(TaskNotFoundHTTPException),
    summary="Отправка кода на проверку",
    description=(
        "Создаёт новую попытку (submission) со статусом `pending` и ставит её "
        "в очередь Celery для выполнения в sandbox. "
        "Для получения результата используйте GET /submissions/{submission_id}."
    ),
)
async def submit_task(
    db: DBDep,
    user_id: UserIdDep,
    task_id: int,
    data: SubmitRequestDTO,
):
    try:
        return await SubmissionsService(db).submit(
            task_id=task_id,
            user_id=user_id,
            data=data,
        )
    except TaskNotFoundException:
        raise TaskNotFoundHTTPException


@router.get(
    "/{task_id}/solution",
    response_model=SolutionDTO,
    status_code=status.HTTP_200_OK,
    responses=generate_responses(
        TaskNotFoundHTTPException,
        SolutionNotFoundHTTPException,
    ),
    summary="Получение финального решения задачи пользователя",
)
async def get_task_solution(db: DBDep, user_id: UserIdDep, task_id: int):
    try:
        return await TasksService(db).get_task_solution(
            task_id=task_id, user_id=user_id
        )
    except TaskNotFoundException:
        raise TaskNotFoundHTTPException
    except SolutionNotFoundException:
        raise SolutionNotFoundHTTPException
