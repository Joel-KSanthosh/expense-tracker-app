from typing import Any

from backend.app.core.jwt import create_access_token, create_refresh_token, decode_refresh_token
from backend.app.core.password_hasher import hash_password, verify_password
from backend.app.dtos.request_dto import RefreshTokenRequest, UserCreate, UserLogin
from backend.app.dtos.response_dto import TokenResponse, UserResponse
from backend.app.errors import AppError
from backend.app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, user_repo: UserRepository) -> None:
        self._users: UserRepository = user_repo

    async def create_user(self, user: UserCreate):
        data: dict[str, Any] = user.model_dump(exclude={"password", "confirm_password"})
        data["password"] = await hash_password(password=user.password.get_secret_value())
        await self._users.create(data=data)

    async def login(self, user: UserLogin) -> TokenResponse:
        data: UserResponse | None = await self._users.get_user_by_email(email=user.email)

        # Define a fake hash to trigger the full hashing loop if user is missing
        fake_hash = "$2b$12$DUMMYHASHFORTIMINGATTACKSPREVENTION"

        # Select the target hash, defaulting to fake if data is None
        target_hash = data.password if data else fake_hash

        # Always verify the password to guarantee consistent execution time
        status: bool = await verify_password(user.password, hashed=target_hash)

        # Generic error message prevents revealing user existence
        if not data or not status:
            raise AppError(message="Invalid email or password", status_code=401)

        return TokenResponse(
            access_token=create_access_token(subject=user.email),
            refresh_token=create_refresh_token(subject=user.email),
        )

    def refresh(self, data: RefreshTokenRequest) -> TokenResponse:
        subject = decode_refresh_token(data.refresh_token)
        return TokenResponse(
            access_token=create_access_token(subject=subject),
            refresh_token=create_refresh_token(subject=subject),
        )
