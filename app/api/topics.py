from fastapi import APIRouter, status

from app.api.deps.auth import UserIdDep
from app.api.deps.db import DBDep
from app.api.responses import generate_responses
from app.exceptions.excs import TaskNotFoundException, TopicNotFoundException
from app.exceptions.http_excs import (
    TaskNotFoundHTTPException,
    TopicNotFoundHTTPException,
)
from app.schemas.tasks import TaskBriefDTO
from app.schemas.topics import TopicDetailDTO, TopicDTO
from app.services.topics import TopicsService

router = APIRouter(prefix="/topics", tags=["Темы"])


@router.get(
    "",
    response_model=list[TopicDTO],
    status_code=status.HTTP_200_OK,
    summary="Получение списка всех тем",
)
async def get_all_topics(db: DBDep, _: UserIdDep):
    return await TopicsService(db).get_all_topics()


@router.get(
    "/{topic_id}",
    response_model=TopicDetailDTO,
    status_code=status.HTTP_200_OK,
    responses=generate_responses(TopicNotFoundHTTPException),
    summary="Получение темы с теорией",
)
async def get_topic(db: DBDep, _: UserIdDep, topic_id: int):
    try:
        return await TopicsService(db).get_topic_by_id(topic_id)
    except TopicNotFoundException:
        raise TopicNotFoundHTTPException


@router.get(
    "/{topic_id}/tasks",
    response_model=list[TaskBriefDTO],
    status_code=status.HTTP_200_OK,
    responses=generate_responses(TaskNotFoundHTTPException),
    summary="Получение задач по теме",
)
async def get_tasks_by_topic(db: DBDep, _: UserIdDep, topic_id: int):
    try:
        return await TopicsService(db).get_tasks_by_topic(topic_id)
    except TaskNotFoundException:
        raise TaskNotFoundHTTPException
