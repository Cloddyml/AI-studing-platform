from app.exceptions.excs import (
    ObjectNotFoundException,
    UserNotFoundException,
)
from app.schemas.stats import UserStatsDTO
from app.schemas.users import (
    UserHashedPasswordOnlyDTO,
    UserPasswordOnlyDTO,
    UserUpdateRequestPatchDTO,
)
from app.schemas.users_progresses import UserProgressDTO
from app.services.base import BaseService
from app.services.utils import hash_password


class UsersService(BaseService):
    async def partial_update_user(
        self,
        user_id: int,
        user_data: UserUpdateRequestPatchDTO,
    ):
        try:
            await self.db.users.edit(user_data, exclude_unset=True, id=user_id)
            await self.db.commit()
        except ObjectNotFoundException:
            raise UserNotFoundException

    async def update_user_password(
        self,
        user_id: int,
        user_password_data: UserPasswordOnlyDTO,
    ):
        user_hashed_password_data = UserHashedPasswordOnlyDTO(
            hashed_password=hash_password(password=user_password_data.password)
        )
        try:
            await self.db.users.edit(
                user_hashed_password_data, exclude_unset=True, id=user_id
            )
            await self.db.commit()
        except ObjectNotFoundException:
            raise UserNotFoundException

    async def get_progress(self, user_id: int) -> list[UserProgressDTO]:
        """Прогресс пользователя по всем темам, в которых он решал задачи."""
        return await self.db.users_progresses.get_user_progress(user_id)

    async def get_stats(self, user_id: int) -> UserStatsDTO:
        """Агрегированная статистика для профиля пользователя."""
        total_tasks_solved = await self.db.solutions.count_by_user(user_id)
        total_submissions = await self.db.submissions.count_by_user(user_id)
        topics_completed = await self.db.users_progresses.count_completed(user_id)

        # success_rate = процент попыток, приведших к правильному ответу
        if total_submissions > 0:
            success_rate = round(total_tasks_solved / total_submissions * 100, 1)
        else:
            success_rate = 0.0

        return UserStatsDTO(
            total_tasks_solved=total_tasks_solved,
            total_submissions=total_submissions,
            topics_completed=topics_completed,
            success_rate=success_rate,
        )
