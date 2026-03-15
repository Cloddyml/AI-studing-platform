from app.models.ai_interactions import AIInteractionsOrm
from app.models.refresh_tokens import RefreshTokensOrm
from app.models.solutions import SolutionsOrm
from app.models.submissions import SubmissionsOrm
from app.models.task_tests import TaskTestsOrm
from app.models.tasks import TasksOrm
from app.models.topics import TopicsOrm
from app.models.users import UsersOrm
from app.models.users_progresses import UsersProgressesOrm
from app.repositories.mappers.base import DataMapper
from app.schemas.ai_interactions import AIInteractionDTO
from app.schemas.refresh_tokens import RefreshTokenDTO
from app.schemas.solutions import SolutionDTO
from app.schemas.submissions import SubmissionDTO
from app.schemas.task_tests import TaskTestDTO
from app.schemas.tasks import TaskBriefDTO, TaskDetailDTO
from app.schemas.topics import TopicDetailDTO, TopicDTO
from app.schemas.users import UserDTO, UserWithHashedPasswordDTO
from app.schemas.users_progresses import UserProgressDTO


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


class TaskTestDataMapper(DataMapper):
    db_model = TaskTestsOrm
    schema = TaskTestDTO


class SolutionDataMapper(DataMapper):
    db_model = SolutionsOrm
    schema = SolutionDTO


class SubmissionDataMapper(DataMapper):
    db_model = SubmissionsOrm
    schema = SubmissionDTO


class UserProgressDataMapper(DataMapper):
    db_model = UsersProgressesOrm
    schema = UserProgressDTO


class AIInteractionDataMapper(DataMapper):
    db_model = AIInteractionsOrm
    schema = AIInteractionDTO
