import abc
from typing import Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import select

from db.database import Base, DatabaseSessionManager

Entity = TypeVar("Entity", bound="Base")


class BaseRepo(abc.ABC):
    _model: Type[BaseModel] | None = None

    def __init__(self, session_manager: DatabaseSessionManager):
        if self._model is None:
            raise AttributeError(f"Missing '_model' attribute in {self.__class__.__name__}")

        self.session_manager = session_manager

    async def create(self, entity: Entity) -> Entity:
        async with self.session_manager.session() as db:
            db.add(entity)
            await db.commit()
            await db.refresh(entity)
            return entity

    async def get_list(self) -> list[Entity]:
        async with self.session_manager.session() as db:
            return (await db.execute(select(self._model))).scalars().all()  # type: ignore

    async def get_by(self, **kwargs) -> list[Entity]:
        async with self.session_manager.session() as db:
            return (await db.execute(select(self._model).filter_by(**kwargs))).scalars().first()  # type: ignore

    async def filter_by(self, **kwargs) -> list[Entity]:
        async with self.session_manager.session() as db:
            return (await db.execute(select(self._model).filter_by(**kwargs))).scalars().all()  # type: ignore

    async def update(self, entity: Entity, **update_data) -> None:
        async with self.session_manager.session() as db:
            entity = await db.merge(entity)
            for field, value in update_data.items():
                setattr(entity, field, value)
            await db.commit()

    async def delete(self, entity: Entity) -> None:
        async with self.session_manager.session() as db:
            await db.delete(entity)
            await db.commit()
