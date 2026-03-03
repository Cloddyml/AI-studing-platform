from typing import TypeVar

from pydantic import BaseModel

from app.core.database import Base

SchemaType = TypeVar("SchemaType", bound=BaseModel)


class DataMapper:
    db_model: type[Base]
    schema: type[SchemaType]  # type: ignore

    @classmethod
    def map_to_domain_entity(cls, data):
        return cls.schema.model_validate(data, from_attributes=True)

    @classmethod
    def map_to_persistence_entity(cls, data):
        return cls.db_model(**data.model_dump())
