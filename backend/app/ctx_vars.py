import logging
from contextvars import ContextVar
from typing import Literal

request_id_ctx: ContextVar[str] = ContextVar[str]("request_id", default="-")


class RequestIdFilter(logging.Filter):
    def filter(self, record) -> Literal[True]:
        record.request_id = request_id_ctx.get()
        return True
