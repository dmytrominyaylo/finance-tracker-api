from app.exceptions.base import NotFoundException
from app.schemas.budget import BudgetCreate, BudgetUpdate


class BudgetService:
    def __init__(self, session, repo, category_repo):
        self._session = session
        self._repo = repo
        self._category_repo = category_repo

    async def create_budget(self, payload: BudgetCreate, current_user_id: int):
        category = await self._category_repo.get_by_id_and_user(payload.category_id, current_user_id)

        if not category:
            raise NotFoundException("Category not found")

        budget_data = {
            "user_id": current_user_id,
            "category_id": payload.category_id,
            "limit_amount": payload.limit_amount,
            "period": payload.period,
            "month": payload.month,
        }

        budget = await self._repo.create(budget_data)

        await self._session.commit()

        return budget

    async def get_budget_by_id(self, budget_id: int, current_user_id: int):
        budget = await self._repo.get_by_id_and_user(budget_id, current_user_id)

        if not budget:
            raise NotFoundException("Budget not found")

        return budget

    async def get_all_budgets(self, current_user_id: int, offset: int = 0, limit: int = 100):
        budgets = await self._repo.get_by_user(current_user_id, offset=offset, limit=limit)

        return {"budgets": budgets, "total": len(budgets)}

    async def update_budget(self, budget_id: int, payload: BudgetUpdate, current_user_id: int):
        budget = await self._repo.get_by_id_and_user(budget_id, current_user_id)

        if not budget:
            raise NotFoundException("Budget not found")

        update_data = {}

        if payload.category_id is not None:
            category = await self._category_repo.get_by_id_and_user(payload.category_id, current_user_id)
            if not category:
                raise NotFoundException("Category not found")
            update_data["category_id"] = payload.category_id

        if payload.limit_amount is not None:
            update_data["limit_amount"] = payload.limit_amount

        if payload.period is not None:
            update_data["period"] = payload.period

        if payload.month is not None:
            update_data["month"] = payload.month

        budget = await self._repo.update(budget_id, update_data)

        await self._session.commit()

        return budget

    async def delete_budget(self, budget_id: int, current_user_id: int):
        budget = await self._repo.get_by_id_and_user(budget_id, current_user_id)

        if not budget:
            raise NotFoundException("Budget not found")

        await self._repo.delete(budget_id)

        await self._session.commit()
