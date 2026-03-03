from app.models.users import UsersOrm
from app.repositories.mappers.base import DataMapper
from app.schemas.users import UserDTO


class UserDataMapper(DataMapper):
    db_model = UsersOrm
    schema = UserDTO
