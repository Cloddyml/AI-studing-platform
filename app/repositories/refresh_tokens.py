from sqlalchemy import update

from app.models.refresh_tokens import RefreshTokensOrm
from app.repositories.base import BaseRepository
from app.repositories.mappers.mappers import RefreshTokenDataMapper


class RefreshTokensRepository(BaseRepository):
    model = RefreshTokensOrm
    mapper = RefreshTokenDataMapper

    async def get_valid_token(self, hashed_token: str):
        """Найти токен, который не отозван и не истёк."""
        return await self.get_one_or_none(
            hashed_token=hashed_token,
            revoked=False,
        )

    async def revoke_token(self, hashed_token: str) -> None:
        """Отозвать конкретный токен (logout)."""
        stmt = (
            update(self.model).filter_by(hashed_token=hashed_token).values(revoked=True)
        )
        await self.session.execute(stmt)

    async def revoke_all_user_tokens(self, user_id: int) -> None:
        """Отозвать все токены пользователя (смена пароля / force logout)."""
        stmt = (
            update(self.model)
            .filter_by(user_id=user_id, revoked=False)
            .values(revoked=True)
        )
        await self.session.execute(stmt)
