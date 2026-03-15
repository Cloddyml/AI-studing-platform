from app.exceptions.excs import SubmissionNotFoundException, TaskNotFoundException
from app.schemas.submissions import (
    SubmissionAddDTO,
    SubmissionDTO,
    SubmitRequestDTO,
    SubmitResponseDTO,
)
from app.services.base import BaseService


class SubmissionsService(BaseService):
    async def submit(
        self,
        task_id: int,
        user_id: int,
        data: SubmitRequestDTO,
    ) -> SubmitResponseDTO:
        """
        Создаёт запись Submission со статусом PENDING и ставит задачу в Celery.

        Полинг результата: GET /submissions/{submission_id}
        """
        # 1. Проверяем, что задача существует и опубликована
        task = await self.db.tasks.get_published_by_id(task_id)
        if task is None:
            raise TaskNotFoundException

        # 2. Создаём submission
        add_dto = SubmissionAddDTO(
            user_id=user_id,
            task_id=task_id,
            code=data.code,
        )
        submission = await self.db.submissions.add(add_dto)
        await self.db.commit()

        # 3. Ставим задачу в очередь Celery
        # Импорт внутри метода — избегаем циклических зависимостей при старте приложения
        from app.worker.tasks import execute_submission

        execute_submission.delay(submission.id)

        return SubmitResponseDTO(
            submission_id=submission.id,
            status=submission.status,
        )

    async def get_submission(
        self,
        submission_id: int,
        user_id: int,
    ) -> SubmissionDTO:
        """
        Получить статус конкретной попытки пользователя.
        user_id обязателен — нельзя смотреть чужие submission'ы.
        """
        submission = await self.db.submissions.get_user_submission(
            user_id=user_id,
            submission_id=submission_id,
        )
        if submission is None:
            raise SubmissionNotFoundException
        return submission
