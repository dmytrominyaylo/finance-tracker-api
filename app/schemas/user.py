from datetime import datetime
from typing import List, Optional
from pydantic import Field
from app.schemas.base import BasePydanticModel


class UserCreate(BasePydanticModel):
    email: str
    password: str = Field(min_length=6, max_length=72)


class UserUpdate(BasePydanticModel):
    email: Optional[str] = None
    password: Optional[str] = Field(default=None, min_length=6, max_length=72)


class UserRead(BasePydanticModel):
    id: int
    email: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserList(BasePydanticModel):
    total: int
    users: List[UserRead]
