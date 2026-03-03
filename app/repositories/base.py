from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base


class BaseRepository:
    model: type[Base]
    mapper: type[DataMapper]
    session: AsyncSession

    def __init__(self, session: AsyncSession):
        self.session = session
