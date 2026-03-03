from datetime import datetime, timezone

from sqlalchemy import delete as sa_delete
from sqlalchemy import select, update

from app.models.refresh_tokens import RefreshTokensOrm
from app.repositories.base import BaseRepository
from app.repositories.mappers.mappers import RefreshTokenDataMapper


class RefreshTokensRepository(BaseRepository):
    model = RefreshTokensOrm
    mapper = RefreshTokenDataMapper

    async def get_valid_token(self, hashed_token: str):
        """Найти токен, который не отозван и не истёк."""
        now = datetime.now(timezone.utc)
        query = (
            select(self.model)
            .filter_by(
                hashed_token=hashed_token,
                revoked=False,
            )
            .where(self.model.expires_at > now)
        )
        result = await self.session.execute(query)
        obj = result.scalars().one_or_none()
        if obj is None:
            return None
        return self.mapper.map_to_domain_entity(obj)

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

    async def delete_expired_tokens(self, user_id: int) -> None:
        """Удалить все истёкшие и отозванные токены пользователя."""
        now = datetime.now(timezone.utc)
        stmt = sa_delete(self.model).where(
            self.model.user_id == user_id,
            (self.model.expires_at < now) | (self.model.revoked == True),
        )
        await self.session.execute(stmt)
