from sqlalchemy import select

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
