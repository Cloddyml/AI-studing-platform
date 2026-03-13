from app.models.users import UsersOrm
from app.repositories.base import BaseRepository
from app.repositories.mappers.mappers import UserWithHashedPasswordDataMapper
from app.schemas.users import UserWithHashedPasswordDTO


class UsersRepository(BaseRepository):
    model = UsersOrm
    mapper = UserWithHashedPasswordDataMapper

    async def get_user_with_hashed_password(
        self, email: str
    ) -> UserWithHashedPasswordDTO | None:
        return await self.get_one_or_none(email=email)

    async def get_user_by_id(self, user_id: int) -> UserWithHashedPasswordDTO | None:
        return await self.get_one_or_none(id=user_id)
