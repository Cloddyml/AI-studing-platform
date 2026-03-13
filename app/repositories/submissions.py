from app.models.submissions import SubmissionsOrm
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
        return await self.get_one_or_none(id=submission_id, user_id=user_id)
