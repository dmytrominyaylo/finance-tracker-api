from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from pydantic import field_validator

from app.schemas.base import BasePydanticModel


class TransactionType(str, Enum):
    income = "income"
    expense = "expense"


class TransactionCreate(BasePydanticModel):
    category_id: int
    amount: Decimal
    type: TransactionType
    description: str | None = None
    transaction_date: date

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, value: Decimal) -> Decimal:
        if value <= 0:
            raise ValueError("Amount must be greater than 0")
        return value


class TransactionUpdate(BasePydanticModel):
    category_id: int | None = None
    amount: Decimal | None = None
    type: TransactionType | None = None
    description: str | None = None
    transaction_date: date | None = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Decimal | None) -> Decimal | None:
        if v is not None and v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v


class TransactionRead(BasePydanticModel):
    id: int
    user_id: int
    category_id: int
    amount: Decimal
    type: TransactionType
    description: str | None
    transaction_date: date
    created_at: datetime
    updated_at: datetime


class TransactionList(BasePydanticModel):
    total: int
    transactions: list[TransactionRead]
