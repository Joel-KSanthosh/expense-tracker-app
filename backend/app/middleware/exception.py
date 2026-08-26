import logging
from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.app.errors import AppError

logger = logging.getLogger(__name__)


def _get_error_response(
    status: int,
    code: str,
    message: str,
    **extra: Any,
) -> JSONResponse:
    body: dict[str, Any] = {
        "error": {
            "code": code,
            "message": message,
        },
    }

    if extra:
        body["error"].update(extra)

    return JSONResponse(
        status_code=status,
        content=body,
    )


async def handle_exception(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    if isinstance(exc, AppError):
        return _get_error_response(
            status=exc.status_code,
            code=exc.code,
            message=exc.message,
        )

    if isinstance(exc, RequestValidationError):
        return _get_error_response(
            status=422,
            code="validation_error",
            message="Request validation failed",
            details=exc.errors(),
        )

    if isinstance(exc, StarletteHTTPException):
        return _get_error_response(
            status=exc.status_code,
            code="http_error",
            message=str(exc.detail),
        )

    return _get_error_response(
        status=500,
        code="internal_error",
        message="Internal server error",
    )
