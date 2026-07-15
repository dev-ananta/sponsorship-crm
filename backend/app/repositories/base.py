from collections.abc import Sequence
from typing import Generic, TypeVar

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def get(self, entity_id: int) -> ModelType | None:
        stmt: Select[tuple[ModelType]] = select(self.model).where(
            self.model.id == entity_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        stmt: Select[tuple[ModelType]] = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, payload: dict) -> ModelType:
        instance = self.model(**payload)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update(self, instance: ModelType, payload: dict) -> ModelType:
        for key, value in payload.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, entity_id: int) -> ModelType | None:
        instance = await self.get(entity_id)
        if instance is None:
            return None

        await self.session.delete(instance)
        await self.session.flush()
        return instance
