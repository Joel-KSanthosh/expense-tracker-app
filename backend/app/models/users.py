from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    f_name: Mapped[str] = mapped_column(String(length=100), nullable=False)

    m_name: Mapped[str] = mapped_column(String(length=100), default="", nullable=True)

    l_name: Mapped[str] = mapped_column(String(length=100), nullable=False)

    email: Mapped[str] = mapped_column(String(length=255), unique=True, nullable=False, index=True)

    password: Mapped[str] = mapped_column(String(length=255), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(tz=timezone.utc), nullable=False
    )

    modified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(tz=timezone.utc),
        onupdate=lambda: datetime.now(tz=timezone.utc),
        nullable=False,
    )
