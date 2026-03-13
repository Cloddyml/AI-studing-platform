import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings
from app.exceptions.excs import (
    EmailNotRegisteredException,
    IncorrectPasswordException,
    IncorrectTokenException,
    ObjectAlreadyExistsException,
    ObjectNotFoundException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from app.schemas.refresh_tokens import RefreshTokenAddDTO
from app.schemas.users import UserAddDTO, UserLoginDTO, UserRequestAddDTO
from app.services.base import BaseService
from app.services.utils import hash_password, verify_password


class AuthService(BaseService):
    def create_access_token(self, data: dict) -> str:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        return jwt.encode(
            {**data, "exp": expire},
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

    @staticmethod
    def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
        except jwt.exceptions.DecodeError:
            raise IncorrectTokenException
        except jwt.exceptions.ExpiredSignatureError:
            raise IncorrectTokenException

    def _generate_refresh_token(self) -> str:
        """Сгенерировать криптографически безопасный raw-токен."""
        return secrets.token_urlsafe(64)

    def _hash_refresh_token(self, raw_token: str) -> str:
        """SHA-256 хэш — то, что ложится в БД."""
        return hashlib.sha256(raw_token.encode()).hexdigest()

    async def _save_refresh_token(self, user_id: int, raw_token: str) -> None:
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        token_data = RefreshTokenAddDTO(
            user_id=user_id,
            hashed_token=self._hash_refresh_token(raw_token),
            expires_at=expires_at,
        )
        await self.db.refresh_tokens.add(token_data)

    async def register_user(self, data: UserRequestAddDTO) -> None:
        hashed_password = hash_password(data.password)
        new_user_data = UserAddDTO(
            email=data.email,
            username=data.username,
            hashed_password=hashed_password,
        )
        try:
            await self.db.users.add(new_user_data)
            await self.db.commit()
        except ObjectAlreadyExistsException as ex:
            raise UserAlreadyExistsException from ex

    async def login_user(self, data: UserLoginDTO) -> tuple[str, str]:
        """Вернуть (access_token, refresh_token)."""
        user = await self.db.users.get_user_with_hashed_password(email=data.email)
        if not user:
            raise EmailNotRegisteredException
        if not verify_password(data.password, user.hashed_password):
            raise IncorrectPasswordException

        await self.db.refresh_tokens.delete_all_user_tokens(user.id)

        access_token = self.create_access_token({"user_id": user.id, "role": user.role})
        raw_refresh = self._generate_refresh_token()
        await self._save_refresh_token(user.id, raw_refresh)
        await self.db.commit()

        return access_token, raw_refresh

    async def refresh_access_token(self, raw_refresh_token: str) -> tuple[str, str]:
        """
        Проверить refresh-токен, отозвать старый, выдать новую пару.
        Реализует token rotation — старый токен сразу становится невалидным.
        """
        hashed = self._hash_refresh_token(raw_refresh_token)
        token_record = await self.db.refresh_tokens.get_valid_token(hashed)

        if token_record is None:
            raise IncorrectTokenException

        user = await self.db.users.get_user_by_id(token_record.user_id)
        if user is None:
            raise IncorrectTokenException

        await self.db.refresh_tokens.delete_all_user_tokens(token_record.user_id)

        new_access = self.create_access_token(
            {
                "user_id": token_record.user_id,
                "role": user.role,
            }
        )
        new_raw_refresh = self._generate_refresh_token()
        await self._save_refresh_token(token_record.user_id, new_raw_refresh)
        await self.db.commit()

        return new_access, new_raw_refresh

    async def logout_user(self, raw_refresh_token: str) -> None:
        hashed = self._hash_refresh_token(raw_refresh_token)
        await self.db.refresh_tokens.revoke_token(hashed)
        await self.db.commit()

    async def get_one_or_none_user(self, user_id: int):
        return await self.db.users.get_one_or_none(id=user_id)

    async def delete_user(self, user_id: int):
        try:
            await self.db.users.delete(id=user_id)
            await self.db.commit()

        except ObjectNotFoundException as ex:
            raise UserNotFoundException from ex
