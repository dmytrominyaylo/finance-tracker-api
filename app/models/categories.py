from datetime import datetime

from sqlalchemy import Index, Integer, ForeignKey, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (
        Index(
            "categories_user_name_idx",
            "user_id",
            "name"
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    user = relationship(
        "User",
        back_populates="categories",
        lazy="raise"
    )

    transactions = relationship(
        "Transaction",
        back_populates="category",
        lazy="raise"
    )

    budgets = relationship(
        "Budget",
        back_populates="category",
        lazy="raise"
    )
