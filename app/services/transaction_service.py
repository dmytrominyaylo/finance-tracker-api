from app.exceptions.base import NotFoundException
from app.schemas.transaction import TransactionCreate, TransactionUpdate


class TransactionService:
    def __init__(self, session, repo, category_repo):
        self._session = session
        self._repo = repo
        self._category_repo = category_repo

    async def create_transaction(self, payload: TransactionCreate, current_user_id: int):
        category = await self._category_repo.get_by_id_and_user(payload.category_id, current_user_id)

        if not category:
            raise NotFoundException("Category not found")

        transaction_data = {
            "user_id": current_user_id,
            "category_id": payload.category_id,
            "amount": payload.amount,
            "type": payload.type,
            "description": payload.description,
            "transaction_date": payload.transaction_date,
        }

        transaction = await self._repo.create(transaction_data)

        await self._session.commit()

        return transaction

    async def get_transaction_by_id(self, transaction_id: int, current_user_id: int):
        transaction = await self._repo.get_by_id_and_user(transaction_id, current_user_id)

        if not transaction:
            raise NotFoundException("Transaction not found")

        return transaction

    async def get_all_transactions(self, current_user_id: int, offset: int = 0, limit: int = 100):
        transactions = await self._repo.get_by_user(current_user_id, offset=offset, limit=limit)

        return {"transactions": transactions, "total": len(transactions)}

    async def update_transaction(self, transaction_id: int, payload: TransactionUpdate, current_user_id: int):
        transaction = await self._repo.get_by_id_and_user(transaction_id, current_user_id)

        if not transaction:
            raise NotFoundException("Transaction not found")

        update_data = {}

        if payload.category_id is not None:
            category = await self._category_repo.get_by_id_and_user(payload.category_id, current_user_id)
            if not category:
                raise NotFoundException("Category not found")
            update_data["category_id"] = payload.category_id

        if payload.amount is not None:
            update_data["amount"] = payload.amount

        if payload.type is not None:
            update_data["type"] = payload.type

        if payload.description is not None:
            update_data["description"] = payload.description

        if payload.transaction_date is not None:
            update_data["transaction_date"] = payload.transaction_date

        transaction = await self._repo.update(transaction_id, update_data)

        await self._session.commit()

        return transaction

    async def delete_transaction(self, transaction_id: int, current_user_id: int):
        transaction = await self._repo.get_by_id_and_user(transaction_id, current_user_id)

        if not transaction:
            raise NotFoundException("Transaction not found")

        await self._repo.delete(transaction_id)

        await self._session.commit()
