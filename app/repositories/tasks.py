from sqlalchemy import select

from app.models.tasks import TasksOrm
from app.repositories.base import BaseRepository
from app.repositories.mappers.mappers import TaskBriefDataMapper, TaskDetailDataMapper
from app.schemas.tasks import TaskBriefDTO, TaskDetailDTO


class TasksRepository(BaseRepository):
    model = TasksOrm
    mapper = TaskBriefDataMapper
    brief_mapper = TaskBriefDataMapper
    detail_mapper = TaskDetailDataMapper

    async def get_published_by_topic(self, topic_id: int) -> list[TaskBriefDTO]:
        query = (
            select(self.model)
            .filter_by(topic_id=topic_id, is_published=True)
            .order_by(self.model.order_index)
        )
        result = await self.session.execute(query)
        return [
            self.brief_mapper.map_to_domain_entity(row)
            for row in result.scalars().all()
        ]

    async def get_published_by_id(self, task_id: int) -> TaskDetailDTO | None:
        query = select(self.model).filter_by(id=task_id, is_published=True)
        result = await self.session.execute(query)
        row = result.scalars().one_or_none()
        if row is None:
            return None
        return self.detail_mapper.map_to_domain_entity(row)
