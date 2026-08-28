from datetime import datetime, timedelta, timezone

import jwt

from backend.app.config import get_settings
from backend.app.errors import AppError


def create_access_token(subject: str) -> str:
    settings = get_settings()
    return _create_token(
        subject=subject,
        token_type="access",
        expires_delta=timedelta(minutes=settings.jwt.access_expire_minutes),
    )


def create_refresh_token(subject: str) -> str:
    settings = get_settings()
    return _create_token(
        subject=subject,
        token_type="refresh",
        expires_delta=timedelta(days=settings.jwt.refresh_expire_days),
    )


def _create_token(subject: str, token_type: str, expires_delta: timedelta) -> str:
    settings = get_settings()
    expires_at = datetime.now(tz=timezone.utc) + expires_delta
    payload = {"sub": subject, "type": token_type, "exp": expires_at}
    return jwt.encode(payload, settings.jwt.secret_key, algorithm=settings.jwt.algorithm)


def decode_access_token(token: str) -> str:
    return _decode_token(token=token, expected_type="access")


def decode_refresh_token(token: str) -> str:
    return _decode_token(token=token, expected_type="refresh")


def _decode_token(token: str, expected_type: str) -> str:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt.secret_key, algorithms=[settings.jwt.algorithm])
    except jwt.InvalidTokenError as exc:
        raise AppError(message="Could not validate credentials", status_code=401) from exc

    subject = payload.get("sub")
    if payload.get("type") != expected_type or not isinstance(subject, str) or not subject:
        raise AppError(message="Could not validate credentials", status_code=401)

    return subject
