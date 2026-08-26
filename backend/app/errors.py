class AppError(Exception):
    status_code: int = 400
    code: str = "app_error"

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        self.message: str = message
        if status_code is not None:
            self.status_code = status_code
        super().__init__(message)


class InternalServerError(AppError):
    status_code = 500
    code = "internal_error"


class ConfigurationError(AppError):
    status_code = 500
    code = "configuration_error"


class UpstreamAuthError(AppError):
    status_code = 502
    code = "upstream_auth_failed"


class UpstreamTimeoutError(AppError):
    status_code = 504
    code = "upstream_timeout"
