from collections.abc import AsyncGenerator

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio.session import AsyncSession

from backend.app.core.jwt import decode_access_token
from backend.app.database import Database
from backend.app.services.user_service import UserService

bearer_scheme = HTTPBearer()


async def get_session(request: Request) -> AsyncGenerator[AsyncSession]:
    db: Database = request.app.state.db
    async with db.session() as session:
        yield session


async def get_user_service(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> UserService:
    container = request.app.container  # type: ignore[attr-defined]
    return container.services.user(
        user_repo=container.services.repositories.user_repository(session=session),
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    return decode_access_token(credentials.credentials)
