# database.py
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

logger = logging.getLogger(__name__)


class Database:
    """Manages the SQLAlchemy async engine and session lifecycle."""

    def __init__(self, dsn: str, min_size: int = 5, max_size: int = 20, echo: bool = False) -> None:
        self.dsn: str = dsn
        self.min_size: int = min_size
        self.max_size: int = max_size
        self.echo: bool = echo
        self._engine: AsyncEngine | None = None
        self._sessionmaker: async_sessionmaker[AsyncSession] | None = None

    async def connect(self) -> None:
        if self._engine is not None:
            return
        self._engine = create_async_engine(
            url=self.dsn,
            echo=self.echo,
            pool_size=self.min_size,
            max_overflow=self.max_size - self.min_size,
            pool_pre_ping=True,
            pool_recycle=1800,
        )
        self._sessionmaker = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
        )
        logger.info("Database engine created")

    async def disconnect(self) -> None:
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._sessionmaker = None
            logger.info("Database engine disposed")

    @property
    def engine(self) -> AsyncEngine:
        if self._engine is None:
            raise RuntimeError("Database engine is not initialized. Call connect() first.")
        return self._engine

    @property
    def sessionmaker(self) -> async_sessionmaker[AsyncSession]:
        if self._sessionmaker is None:
            raise RuntimeError("Database engine is not initialized. Call connect() first.")
        return self._sessionmaker

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession]:
        """Returns an async context manager yielding a session (with rollback on error)."""
        async with self.sessionmaker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
