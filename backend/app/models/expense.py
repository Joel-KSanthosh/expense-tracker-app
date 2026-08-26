from datetime import date, datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import Date, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models import Base


class Expense(Base):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    category_id: Mapped[UUID] = mapped_column(ForeignKey(column="categories.id"), nullable=False)

    user_id: Mapped[UUID] = mapped_column(ForeignKey(column="users.id"), nullable=False)

    title: Mapped[str] = mapped_column(String(length=100), nullable=False)

    description: Mapped[str] = mapped_column(Text, nullable=True)

    amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    expense_date: Mapped[date] = mapped_column(
        Date, nullable=True, default=lambda: datetime.now(tz=timezone.utc).date()
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(tz=timezone.utc), nullable=False
    )

    modified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(tz=timezone.utc),
        onupdate=lambda: datetime.now(tz=timezone.utc),
        nullable=False,
    )

    __tablename__ = "expenses"
