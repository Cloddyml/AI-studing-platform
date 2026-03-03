from app.models.refresh_tokens import RefreshTokensOrm
from app.models.users import UsersOrm
from app.repositories.mappers.base import DataMapper
from app.schemas.refresh_tokens import RefreshTokenDTO
from app.schemas.users import UserDTO, UserWithHashedPasswordDTO


class UserDataMapper(DataMapper):
    db_model = UsersOrm
    schema = UserDTO


class RefreshTokenDataMapper(DataMapper):
    db_model = RefreshTokensOrm
    schema = RefreshTokenDTO


class UserWithHashedPasswordDataMapper(DataMapper):
    db_model = UsersOrm
    schema = UserWithHashedPasswordDTO
