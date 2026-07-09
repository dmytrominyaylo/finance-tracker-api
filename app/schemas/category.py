from datetime import datetime
from app.schemas.base import BasePydanticModel


class CategoryCreate(BasePydanticModel):
    name: str


class CategoryUpdate(BasePydanticModel):
    name: str


class CategoryRead(BasePydanticModel):
    id: int
    user_id: int
    name: str
    created_at: datetime
    updated_at: datetime


class CategoryList(BasePydanticModel):
    total: int
    categories: list[CategoryRead]
