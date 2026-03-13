from app.models.solutions import SolutionsOrm
from app.repositories.base import BaseRepository
from app.repositories.mappers.mappers import SolutionDataMapper
from app.schemas.solutions import SolutionDTO


class SolutionsRepository(BaseRepository):
    model = SolutionsOrm
    mapper = SolutionDataMapper

    async def get_user_solution(self, user_id: int, task_id: int) -> SolutionDTO | None:
        return await self.get_one_or_none(user_id=user_id, task_id=task_id)
