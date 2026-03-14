from sqlalchemy import select

from app.models.ai_interactions import AIInteractionsOrm
from app.repositories.base import BaseRepository
from app.repositories.mappers.mappers import AIInteractionDataMapper
from app.schemas.ai_interactions import AIInteractionDTO


class AIInteractionsRepository(BaseRepository):
    model = AIInteractionsOrm
    mapper = AIInteractionDataMapper

    async def get_user_interactions(
        self,
        user_id: int,
        limit: int = 50,
    ) -> list[AIInteractionDTO]:
        """Последние `limit` взаимодействий пользователя (для истории / дебага)."""
        query = (
            select(self.model)
            .filter_by(user_id=user_id)
            .order_by(self.model.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return [self.mapper.map_to_domain_entity(row) for row in result.scalars().all()]
