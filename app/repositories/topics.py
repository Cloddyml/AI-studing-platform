from sqlalchemy import select

from app.models.topics import TopicsOrm
from app.repositories.base import BaseRepository
from app.repositories.mappers.mappers import TopicDataMapper, TopicDetailDataMapper
from app.schemas.topics import TopicDetailDTO, TopicDTO


class TopicsRepository(BaseRepository):
    model = TopicsOrm
    mapper = TopicDataMapper
    detail_mapper = TopicDetailDataMapper

    async def get_all_published(self) -> list[TopicDTO]:
        query = (
            select(self.model)
            .filter_by(is_published=True)
            .order_by(self.model.order_index)
        )
        result = await self.session.execute(query)
        return [self.mapper.map_to_domain_entity(row) for row in result.scalars().all()]

    async def get_published_by_id(self, topic_id: int) -> TopicDetailDTO | None:
        query = select(self.model).filter_by(id=topic_id, is_published=True)
        result = await self.session.execute(query)
        row = result.scalars().one_or_none()
        if row is None:
            return None
        return self.detail_mapper.map_to_domain_entity(row)
