from typing import Any

from asyncpg.exceptions import UniqueViolationError
from pydantic import BaseModel
from sqlalchemy import delete as sa_delete
from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base
from app.exceptions.excs import (
    EmptyUpdateDataException,
    ObjectAlreadyExistsException,
    ObjectNotFoundException,
)
from app.repositories.mappers.base import DataMapper


class BaseRepository:
    model: type[Base]
    mapper: type[DataMapper]
    session: AsyncSession

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_filtered(self, *filter, **filter_by) -> list[BaseModel | Any]:
        query = select(self.model).filter(*filter).filter_by(**filter_by)
        result = await self.session.execute(query)
        return [
            self.mapper.map_to_domain_entity(model) for model in result.scalars().all()
        ]

    async def get_all(self, *args, **kwargs) -> list[BaseModel | Any]:
        return await self.get_filtered()

    async def get_one(self, **filter_by) -> BaseModel:
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        try:
            model = result.scalars().one()
        except NoResultFound:
            raise ObjectNotFoundException
        return self.mapper.map_to_domain_entity(model)

    async def get_one_or_none(self, **filter_by) -> BaseModel | None | Any:
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        if model is None:
            return None
        return self.mapper.map_to_domain_entity(model)

    async def add(self, data: BaseModel) -> BaseModel | Any:
        try:
            add_data_stmt = (
                insert(self.model).values(**data.model_dump()).returning(self.model)
            )
            result = await self.session.execute(add_data_stmt)
            model = result.scalars().one()
            return self.mapper.map_to_domain_entity(model)
        except IntegrityError as ex:
            if isinstance(ex.orig.__cause__, UniqueViolationError):  # type: ignore
                raise ObjectAlreadyExistsException from ex
            else:
                raise ex

    async def edit(
        self,
        data: BaseModel,
        exclude_unset: bool = False,
        exclude_none: bool = False,
        **filter_by,
    ) -> None:
        values = data.model_dump(exclude_unset=exclude_unset, exclude_none=exclude_none)
        if not values:
            raise EmptyUpdateDataException

        update_stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**values)
            .returning(self.model.id)
        )
        result = await self.session.execute(update_stmt)
        if result.fetchone() is None:
            raise ObjectNotFoundException

    async def delete(self, **filter_by) -> None:
        delete_stmt = (
            sa_delete(self.model).filter_by(**filter_by).returning(self.model.id)
        )
        result = await self.session.execute(delete_stmt)
        if result.fetchone() is None:
            raise ObjectNotFoundException
