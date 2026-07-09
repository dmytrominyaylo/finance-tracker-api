from sqlalchemy import select

from app.models.transactions import Transaction
from app.repositories.base import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):
    _model = Transaction

    async def get_by_user(
            self,
            user_id: int,
            offset: int = 0,
            limit: int = 100
    ) -> list[Transaction]:

        result = await self._session.execute(
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .order_by(Transaction.transaction_date.desc())
            .offset(offset)
            .limit(limit)
        )

        return result.scalars().all()

    async def get_by_id_and_user(
            self,
            transaction_id: int,
            user_id: int
    ) -> Transaction | None:

        result = await self._session.execute(
            select(Transaction)
            .where(Transaction.id == transaction_id, Transaction.user_id == user_id)
        )

        return result.scalar_one_or_none()
