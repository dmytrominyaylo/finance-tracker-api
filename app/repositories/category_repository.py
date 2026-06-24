from sqlalchemy import select

from app.models.categories import Category
from app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    _model = Category

    async def get_by_user(self, user_id: int, offset: int = 0, limit: int = 100) -> list[Category]:

        result = await self._session.execute(
            select(Category)
            .where(Category.user_id == user_id)
            .order_by(Category.id)
            .offset(offset)
            .limit(limit)
        )

        return result.scalars().all()

    async def get_by_id_and_user(self, category_id: int, user_id: int) -> Category | None:

        result = await self._session.execute(
            select(Category)
            .where(Category.id == category_id, Category.user_id == user_id)
        )

        return result.scalar_one_or_none()
