import asyncio
import logging

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from backend.app.config import get_settings
from backend.app.errors import AppError
from backend.app.logging_config import setup_logging
from backend.app.middleware.exception import StarletteHTTPException, handle_exception
from backend.app.middleware.logging import LoggingMiddleware
from backend.infisical import InfisicalSecretManager

setup_logging()

LOGGER = logging.getLogger(__name__)
settings = get_settings()

app: FastAPI = FastAPI()
app.add_exception_handler(exc_class_or_status_code=AppError, handler=handle_exception)
app.add_exception_handler(exc_class_or_status_code=RequestValidationError, handler=handle_exception)
app.add_exception_handler(exc_class_or_status_code=StarletteHTTPException, handler=handle_exception)
app.add_exception_handler(exc_class_or_status_code=Exception, handler=handle_exception)

app.add_middleware(middleware_class=LoggingMiddleware)


async def get_all_secrets() -> dict[str, str]:
    secret_manager: InfisicalSecretManager = InfisicalSecretManager()
    postgres_password: str = await secret_manager.get_secret(secret_name=settings.postgres.password_secret_name)
    return {"postgres_password": postgres_password}


if __name__ == "__main__":
    data: dict[str, str] = asyncio.run(main=get_all_secrets())
    uvicorn.run(app="backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
