from typing import Any, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

Entity = TypeVar("Entity", bound="Base")


class BaseRepo:
    def __init__(self, db: AsyncSession, model: Any):
        self._db = db
        self._model = model

    async def create(self, entity: Entity) -> Entity:
        self._db.add(entity)
        await self._db.commit()
        await self._db.refresh(entity)
        return entity

    async def get_or_create(self, entity_id: Any, from_dict: dict) -> Entity:
        entity = await self.get_by_id(entity_id)
        return entity or self.create(self._model(**from_dict))
        
    async def get_list(self) -> list[Entity]:
        return (await self._db.execute(select(self._model))).scalars().all()

    async def get_by_id(self, entity_id: Any) -> Entity | None:
        return await self._db.query(self._model).where(self._model.id == entity_id).first()

    async def filter_by(self, **kwargs) -> Entity | None:
        return await self._db.execute(select(self._model).filter_by(**kwargs)).scalar()

    async def update(self, entity: Entity, **update_data) -> None:
        for field, value in update_data.items():
            setattr(entity, field, value)
        await self._db.commit()

    async def delete(self, entity: Entity) -> None:
        await self._db.delete(entity)
        await self._db.commit()
