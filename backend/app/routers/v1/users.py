# routers/users.py
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from backend.app.dependencies import get_current_user, get_user_service
from backend.app.dtos.request_dto import RefreshTokenRequest, UserCreate, UserLogin
from backend.app.dtos.response_dto import TokenResponse
from backend.app.services.user_service import UserService

router = APIRouter()


@router.post(path="/signup", status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    service: UserService = Depends(dependency=get_user_service),
) -> JSONResponse:
    user = await service.create_user(user=data)
    return JSONResponse(content="User created successfully")


@router.post(path="/login", status_code=status.HTTP_200_OK)
async def login_user(
    data: UserLogin,
    service: UserService = Depends(dependency=get_user_service),
) -> TokenResponse:
    user: TokenResponse = await service.login(user=data)
    return user


@router.post(path="/refresh", status_code=status.HTTP_200_OK)
async def refresh_token(
    data: RefreshTokenRequest,
    service: UserService = Depends(dependency=get_user_service),
) -> TokenResponse:
    return service.refresh(data=data)


@router.get(path="/me")
async def get_current_user_details(
    email: str = Depends(dependency=get_current_user),
) -> dict[str, str]:
    return {"email": email}
