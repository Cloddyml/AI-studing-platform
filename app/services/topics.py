from app.exceptions.excs import TaskNotFoundException, TopicNotFoundException
from app.schemas.tasks import TaskBriefDTO
from app.schemas.topics import TopicDetailDTO, TopicDTO
from app.services.base import BaseService


class TopicsService(BaseService):
    async def get_all_topics(self) -> list[TopicDTO]:
        return await self.db.topics.get_all_published()

    async def get_topic_by_id(self, topic_id: int) -> TopicDetailDTO:
        topic = await self.db.topics.get_published_by_id(topic_id)
        if topic is None:
            raise TopicNotFoundException
        return topic

    async def get_tasks_by_topic(self, topic_id: int) -> list[TaskBriefDTO]:
        topic = await self.db.topics.get_published_by_id(topic_id)
        if topic is None:
            raise TopicNotFoundException
        return await self.db.tasks.get_published_by_topic(topic_id)
