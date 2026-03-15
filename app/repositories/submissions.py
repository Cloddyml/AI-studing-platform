from sqlalchemy import func, select

from app.models.submissions import SubmissionsOrm, SubmissionStatus
from app.repositories.base import BaseRepository
from app.repositories.mappers.mappers import SubmissionDataMapper
from app.schemas.submissions import SubmissionDTO


class SubmissionsRepository(BaseRepository):
    model = SubmissionsOrm
    mapper = SubmissionDataMapper

    async def get_by_id(self, submission_id: int) -> SubmissionDTO | None:
        return await self.get_one_or_none(id=submission_id)

    async def get_user_submission(
        self, user_id: int, submission_id: int
    ) -> SubmissionDTO | None:
        """Получить submission конкретного пользователя (защита от чужих данных)."""
        return await self.get_one_or_none(id=submission_id, user_id=user_id)

    async def update_status(
        self,
        submission_id: int,
        status: SubmissionStatus,
        *,
        stdout: str | None = None,
        stderr: str | None = None,
        is_tests_passed: bool | None = None,
    ) -> None:
        """
        Обновляет статус и вывод выполнения.
        Вызывается Celery-воркером в процессе/конце проверки.
        updated_at обновляется автоматически через PostgreSQL-триггер.
        """
        values: dict = {"status": status}
        if stdout is not None:
            values["stdout"] = stdout
        if stderr is not None:
            values["stderr"] = stderr
        if is_tests_passed is not None:
            values["is_tests_passed"] = is_tests_passed

        from sqlalchemy import update

        stmt = update(self.model).where(self.model.id == submission_id).values(**values)
        await self.session.execute(stmt)

    async def count_by_user(self, user_id: int) -> int:
        """Общее количество попыток пользователя (для статистики)."""
        query = select(func.count()).where(self.model.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one()
