from sqlalchemy import func, select, text
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models.solutions import SolutionsOrm
from app.repositories.base import BaseRepository
from app.repositories.mappers.mappers import SolutionDataMapper
from app.schemas.solutions import SolutionAddDTO, SolutionDTO


class SolutionsRepository(BaseRepository):
    model = SolutionsOrm
    mapper = SolutionDataMapper

    async def get_user_solution(self, user_id: int, task_id: int) -> SolutionDTO | None:
        return await self.get_one_or_none(user_id=user_id, task_id=task_id)

    async def count_by_user(self, user_id: int) -> int:
        """Количество уникальных задач, решённых пользователем (для статистики)."""
        query = select(func.count()).where(self.model.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def upsert_solution(self, data: SolutionAddDTO) -> SolutionDTO:
        """
        INSERT ... ON CONFLICT DO UPDATE.

        Если решение уже существует (user_id + task_id = UNIQUE),
        обновляет code и solved_at. Это нужно, потому что студент может
        заново пройти задачу с другим кодом.
        """
        stmt = (
            pg_insert(self.model)
            .values(**data.model_dump())
            .on_conflict_do_update(
                constraint="uq_user_task_solution",
                set_={
                    "code": data.code,
                    "solved_at": text("now()"),
                },
            )
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        return self.mapper.map_to_domain_entity(result.scalars().one())
