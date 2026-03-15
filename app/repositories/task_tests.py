from sqlalchemy import select

from app.models.task_tests import TaskTestsOrm
from app.repositories.base import BaseRepository
from app.repositories.mappers.mappers import TaskTestDataMapper
from app.schemas.task_tests import TaskTestDTO


class TaskTestsRepository(BaseRepository):
    model = TaskTestsOrm
    mapper = TaskTestDataMapper

    async def get_by_task(self, task_id: int) -> list[TaskTestDTO]:
        """
        Возвращает тесты задачи в порядке order_index.
        Видимые (is_hidden=False) и скрытые (is_hidden=True) тесты одинаково
        участвуют в проверке — скрытость влияет только на отображение студенту.
        """
        query = (
            select(self.model)
            .filter_by(task_id=task_id)
            .order_by(self.model.order_index)
        )
        result = await self.session.execute(query)
        return [self.mapper.map_to_domain_entity(row) for row in result.scalars().all()]
