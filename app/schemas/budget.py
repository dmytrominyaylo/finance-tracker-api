from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from pydantic import field_validator

from app.schemas.base import BasePydanticModel


class BudgetPeriod(str, Enum):
    weekly = "weekly"
    monthly = "monthly"
    yearly = "yearly"


class BudgetCreate(BasePydanticModel):
    category_id: int
    limit_amount: Decimal
    period: BudgetPeriod
    month: date

    @field_validator("limit_amount")
    @classmethod
    def limit_amount_must_be_positive(cls, value: Decimal) -> Decimal:
        if value <= 0:
            raise ValueError("Limit amount must be greater than 0")
        return value


class BudgetUpdate(BasePydanticModel):
    category_id: int | None = None
    limit_amount: Decimal | None = None
    period: BudgetPeriod | None = None
    month: date | None = None

    @field_validator("limit_amount")
    @classmethod
    def limit_amount_must_be_positive(cls, value: Decimal | None) -> Decimal | None:
        if value is not None and value <= 0:
            raise ValueError("Limit amount must be greater than 0")
        return value


class BudgetRead(BasePydanticModel):
    id: int
    user_id: int
    category_id: int
    limit_amount: Decimal
    period: BudgetPeriod
    month: date
    created_at: datetime
    updated_at: datetime


class BudgetList(BasePydanticModel):
    total: int
    budgets: list[BudgetRead]
