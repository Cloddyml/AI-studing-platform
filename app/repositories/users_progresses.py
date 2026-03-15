from sqlalchemy import func, select, text
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models.tasks import TasksOrm
from app.models.users_progresses import UsersProgressesOrm
from app.repositories.base import BaseRepository
from app.repositories.mappers.mappers import UserProgressDataMapper
from app.schemas.users_progresses import UserProgressDTO


class UsersProgressesRepository(BaseRepository):
    model = UsersProgressesOrm
    mapper = UserProgressDataMapper

    async def get_user_progress(self, user_id: int) -> list[UserProgressDTO]:
        query = select(self.model).filter_by(user_id=user_id)
        result = await self.session.execute(query)
        return [self.mapper.map_to_domain_entity(row) for row in result.scalars().all()]

    async def get_user_topic_progress(
        self, user_id: int, topic_id: int
    ) -> UserProgressDTO | None:
        return await self.get_one_or_none(user_id=user_id, topic_id=topic_id)

    async def increment_solved(self, user_id: int, topic_id: int) -> None:
        """
        Атомарно создаёт запись прогресса или инкрементирует tasks_solved.

        tasks_total всегда актуализируется через подзапрос — это нужно на случай,
        если после создания прогресса была добавлена новая задача в тему.

        Логика:
        - Если записи нет → INSERT с tasks_solved=1
        - Если есть → UPDATE tasks_solved += 1
        - is_completed = True когда tasks_solved достигает tasks_total
        - completed_at заполняется только при первом завершении
        """
        # Подзапрос: актуальное количество опубликованных задач в теме
        tasks_total_subq = (
            select(func.count())
            .where(TasksOrm.topic_id == topic_id, TasksOrm.is_published.is_(True))
            .scalar_subquery()
        )

        stmt = (
            pg_insert(self.model)
            .values(
                user_id=user_id,
                topic_id=topic_id,
                tasks_total=tasks_total_subq,
                tasks_solved=1,
                is_completed=False,
            )
            .on_conflict_do_update(
                constraint="uq_user_topic",
                set_={
                    "tasks_solved": self.model.tasks_solved + 1,
                    "tasks_total": tasks_total_subq,
                    # is_completed = true когда tasks_solved + 1 >= tasks_total
                    "is_completed": (self.model.tasks_solved + 1) >= tasks_total_subq,
                    # completed_at: ставим now() только при первом завершении
                    "completed_at": text(
                        "CASE WHEN users_progresses.tasks_solved + 1 >= ("
                        "  SELECT COUNT(*) FROM tasks"
                        f"  WHERE topic_id = {topic_id} AND is_published = true"
                        ") AND users_progresses.completed_at IS NULL"
                        "  THEN now()"
                        "  ELSE users_progresses.completed_at"
                        " END"
                    ),
                },
            )
        )
        await self.session.execute(stmt)

    async def count_completed(self, user_id: int) -> int:
        """Количество завершённых тем (для статистики)."""
        query = select(func.count()).where(
            self.model.user_id == user_id,
            self.model.is_completed.is_(True),
        )
        result = await self.session.execute(query)
        return result.scalar_one()
