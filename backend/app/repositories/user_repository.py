from typing import Any

from sqlalchemy import text
from sqlalchemy.engine.result import Result
from sqlalchemy.engine.row import RowMapping
from sqlalchemy.ext.asyncio.session import AsyncSession

from backend.app.dtos.response_dto import UserResponse
from backend.app.models import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def create(self, data: dict[str, object]) -> None:
        user: User = User(**data)
        self._session.add(instance=user)
        await self._session.flush()

    async def get_user_by_email(self, email: str) -> UserResponse | None:
        query = text(
            """
            SELECT f_name, m_name, l_name, password
            FROM users
            WHERE email = :email
            """
        )

        result: Result[Any] = await self._session.execute(query, {"email": email})
        user_data: RowMapping | None = result.mappings().one_or_none()

        if user_data is None:
            return None

        return UserResponse.model_validate(user_data)
