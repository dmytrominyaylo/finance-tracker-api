from app.exceptions.base import NotFoundException
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    def __init__(self, session, repo):
        self._session = session
        self._repo = repo

    async def create_category(self, payload: CategoryCreate, current_user_id: int):
        category_data = {
            "user_id": current_user_id,
            "name": payload.name,
        }

        category = await self._repo.create(category_data)

        await self._session.commit()

        return category

    async def get_category_by_id(self, category_id: int, current_user_id: int):
        category = await self._repo.get_by_id_and_user(category_id, current_user_id)

        if not category:
            raise NotFoundException("Category not found")

        return category

    async def get_all_categories(self, current_user_id: int, offset: int = 0, limit: int = 100):
        categories = await self._repo.get_by_user(current_user_id, offset=offset, limit=limit)

        return {"categories": categories, "total": len(categories)}

    async def update_category(self, category_id: int, payload: CategoryUpdate, current_user_id: int):
        category = await self._repo.get_by_id_and_user(category_id, current_user_id)

        if not category:
            raise NotFoundException("Category not found")

        category = await self._repo.update(category_id, {"name": payload.name})

        await self._session.commit()

        return category

    async def delete_category(self, category_id: int, current_user_id: int):
        category = await self._repo.get_by_id_and_user(category_id, current_user_id)

        if not category:
            raise NotFoundException("Category not found")

        await self._repo.delete(category_id)

        await self._session.commit()
