from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Index, Integer, ForeignKey, Numeric, String, Date, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Budget(Base):
    __tablename__ = "budgets"
    __table_args__ = (
        Index(
            "idx_budget_user_month_category_unique",
            "user_id",
            "month",
            "category_id",
            unique=True
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

    category_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("categories.id"),
        nullable=True
    )

    limit_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    period: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="monthly"
    )

    # Store first day of month (e.g. 2026-06-01)
    month: Mapped[date] = mapped_column(
        Date,
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
        back_populates="budgets",
        lazy="raise"
    )

    category = relationship(
        "Category",
        back_populates="budgets",
        lazy="raise"
    )
