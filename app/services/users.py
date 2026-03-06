from app.exceptions.excs import EmptyUpdateDataException
from app.exceptions.http_excs import EmptyUpdateDataHTTPException
from app.schemas.users import (
    UserHashedPasswordOnlyDTO,
    UserPasswordOnlyDTO,
    UserUpdateRequestPatchDTO,
)
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
        except EmptyUpdateDataException:
            raise EmptyUpdateDataHTTPException

    async def update_user_password(
        self,
        user_id: int,
        user_password_data: UserPasswordOnlyDTO,
    ):
        user_hashed_password_data = UserHashedPasswordOnlyDTO(
            hashed_password=hash_password(password=user_password_data.password)
        )
        await self.db.users.edit(
            user_hashed_password_data, exclude_unset=True, id=user_id
        )
        await self.db.commit()
