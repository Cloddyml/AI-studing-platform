from app.models.refresh_tokens import RefreshTokensOrm
from app.models.solutions import SolutionsOrm
from app.models.tasks import TasksOrm
from app.models.topics import TopicsOrm
from app.models.users import UsersOrm
from app.repositories.mappers.base import DataMapper
from app.schemas.refresh_tokens import RefreshTokenDTO
from app.schemas.solutions import SolutionDTO
from app.schemas.tasks import TaskBriefDTO, TaskDetailDTO
from app.schemas.topics import TopicDetailDTO, TopicDTO
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


class TopicDataMapper(DataMapper):
    db_model = TopicsOrm
    schema = TopicDTO


class TopicDetailDataMapper(DataMapper):
    db_model = TopicsOrm
    schema = TopicDetailDTO


class TaskBriefDataMapper(DataMapper):
    db_model = TasksOrm
    schema = TaskBriefDTO


class TaskDetailDataMapper(DataMapper):
    db_model = TasksOrm
    schema = TaskDetailDTO


class SolutionDataMapper(DataMapper):
    db_model = SolutionsOrm
    schema = SolutionDTO
