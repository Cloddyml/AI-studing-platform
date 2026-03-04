from sqlalchemy import select

from app.models.users import UsersOrm
from app.repositories.base import BaseRepository
from app.repositories.mappers.mappers import (
    UserDataMapper,
    UserWithHashedPasswordDataMapper,
)
from app.schemas.users import UserWithHashedPasswordDTO


class UsersRepository(BaseRepository):
    model = UsersOrm
    mapper = UserDataMapper

    async def get_user_with_hashed_password(
        self, email: str
    ) -> UserWithHashedPasswordDTO | None:
        query = select(self.model).filter_by(email=email)
        result = await self.session.execute(query)
        user_orm = result.scalars().one_or_none()
        if user_orm is None:
            return None
        return UserWithHashedPasswordDataMapper.map_to_domain_entity(user_orm)

    async def get_user_by_id(self, user_id: int) -> UserWithHashedPasswordDTO | None:
        query = select(self.model).filter_by(id=user_id)
        result = await self.session.execute(query)
        user_orm = result.scalars().one_or_none()
        if user_orm is None:
            return None
        return UserWithHashedPasswordDataMapper.map_to_domain_entity(user_orm)
