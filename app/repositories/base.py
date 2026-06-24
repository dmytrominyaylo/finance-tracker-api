from typing import Any, ClassVar, Generic, TypeVar, cast

from sqlalchemy import delete, inspect as sa_inspect, select, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    _model: ClassVar[type]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _pk(self) -> Any:
        return sa_inspect(self._model).mapper.primary_key[0]

    async def get(self, pk: Any) -> ModelT | None:
        result = await self._session.execute(select(self._model).where(self._pk() == pk))
        return result.scalar_one_or_none()

    async def get_many(self, offset: int = 0, limit: int = 100) -> list[ModelT]:
        result = await self._session.execute(select(self._model).order_by(self._pk()).offset(offset).limit(limit))
        return list(result.scalars().all())

    async def create(self, data: dict) -> ModelT:
        instance = self._model(**data)
        self._session.add(instance)
        await self._session.flush()
        await self._session.refresh(instance)
        return instance

    async def update(self, pk: Any, data: dict) -> ModelT | None:
        await self._session.execute(update(self._model).where(self._pk() == pk).values(**data))
        await self._session.flush()
        return await self.get(pk)

    async def delete(self, pk: Any) -> bool:
        result = cast(CursorResult[Any], await self._session.execute(delete(self._model).where(self._pk() == pk)))
        return result.rowcount > 0

    async def exists(self, **filters: Any) -> bool:
        stmt = select(self._model).limit(1)
        for attr, value in filters.items():
            stmt = stmt.where(getattr(self._model, attr) == value)
        result = await self._session.execute(stmt)
        return result.first() is not None
