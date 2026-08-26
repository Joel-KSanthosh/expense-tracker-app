import logging
import time
import uuid
from contextvars import Token

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from backend.app.ctx_vars import request_id_ctx

access_logger: logging.Logger = logging.getLogger(name="log_middleware")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        rid: str = request.headers.get("x-request-id") or str(uuid.uuid4())
        token: Token[str] = request_id_ctx.set(rid)
        start: float = time.perf_counter()
        status = 500
        try:
            response: Response = await call_next(request)
            status: int = response.status_code
            response.headers["x-request-id"] = rid
            access_logger.info(
                "%s %s %s %.1fms",
                request.method,
                request.url.path,
                status,
                (time.perf_counter() - start) * 1000,
                extra={"client": request.client.host if request.client else "-"},
            )
            return response
        except Exception:
            access_logger.exception(
                "%s %s %s %.1fms",
                request.method,
                request.url.path,
                status,
                (time.perf_counter() - start) * 1000,
                extra={"client": request.client.host if request.client else "-"},
            )
            raise
        finally:
            request_id_ctx.reset(token)
