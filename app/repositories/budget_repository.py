from sqlalchemy import select

from app.models.budgets import Budget
from app.repositories.base import BaseRepository


class BudgetRepository(BaseRepository[Budget]):
    _model = Budget

    async def get_by_user(
            self,
            user_id: int,
            offset: int = 0,
            limit: int = 100
    ) -> list[Budget]:

        result = await self._session.execute(
            select(Budget)
            .where(Budget.user_id == user_id)
            .order_by(Budget.month.desc())
            .offset(offset)
            .limit(limit)
        )

        return result.scalars().all()

    async def get_by_id_and_user(
            self,
            budget_id: int,
            user_id: int
    ) -> Budget | None:

        result = await self._session.execute(
            select(Budget)
            .where(Budget.id == budget_id, Budget.user_id == user_id)
        )

        return result.scalar_one_or_none()
