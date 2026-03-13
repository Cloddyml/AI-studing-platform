from app.repositories.refresh_tokens import RefreshTokensRepository
from app.repositories.solutions import SolutionsRepository
from app.repositories.tasks import TasksRepository
from app.repositories.topics import TopicsRepository
from app.repositories.users import UsersRepository


class DBManager:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()
        self.users = UsersRepository(self.session)
        self.refresh_tokens = RefreshTokensRepository(self.session)
        self.topics = TopicsRepository(self.session)
        self.tasks = TasksRepository(self.session)
        self.solutions = SolutionsRepository(self.session)

        return self

    async def __aexit__(self, *args):
        await self.session.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()
