import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from backend.app.config import get_settings
from backend.app.containers import Container
from backend.app.database import Database
from backend.app.errors import AppError
from backend.app.logging_config import setup_logging
from backend.app.middleware.exception import StarletteHTTPException, handle_exception
from backend.app.middleware.logging import LoggingMiddleware
from backend.app.routers import api_router
from backend.infisical import InfisicalSecretManager

setup_logging()

LOGGER = logging.getLogger(__name__)
settings = get_settings()


async def get_all_secrets() -> dict[str, str]:
    secret_manager: InfisicalSecretManager = InfisicalSecretManager()

    names: dict[str, str] = {
        "postgres_password": settings.postgres.password_secret_name,
    }

    values: list[str] = await asyncio.gather(*(secret_manager.get_secret(secret_name=name) for name in names.values()))

    return dict(zip(names.keys(), values))


async def build_config(container: Container) -> None:
    """Fetch secrets once, then push resolved config into the container."""
    secrets: dict[str, str] = await get_all_secrets()

    dsn: str = (
        f"postgresql+asyncpg://{settings.postgres.user}:{secrets['postgres_password']}"
        f"@{settings.postgres.host}:{settings.postgres.port}/{settings.postgres.db}"
    )

    container.config.postgres.dsn.from_value(dsn)
    container.config.postgres.min_size.from_value(5)
    container.config.postgres.max_size.from_value(20)
    container.config.postgres.echo.from_value(False)


def build_database_url(secrets: dict[str, str]) -> str:
    return (
        f"postgresql+asyncpg://{settings.postgres.user}:{secrets['postgres_password']}"
        f"@{settings.postgres.host}:{settings.postgres.port}/{settings.postgres.db}"
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    container = Container()
    await build_config(container)
    app.container = container  # type: ignore[attr-defined]

    db: Database = container.postgres()
    await db.connect()
    app.state.db = db

    yield

    await db.disconnect()


app: FastAPI = FastAPI(lifespan=lifespan)
app.add_exception_handler(exc_class_or_status_code=AppError, handler=handle_exception)
app.add_exception_handler(exc_class_or_status_code=RequestValidationError, handler=handle_exception)
app.add_exception_handler(exc_class_or_status_code=StarletteHTTPException, handler=handle_exception)
app.add_exception_handler(exc_class_or_status_code=Exception, handler=handle_exception)
app.include_router(router=api_router)

app.add_middleware(middleware_class=LoggingMiddleware)


if __name__ == "__main__":
    uvicorn.run(app="backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
