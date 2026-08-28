from fastapi import APIRouter

from backend.app.routers.v1.users import router as user_router

router = APIRouter()

router.include_router(
    router=user_router,
    prefix="/user",
    tags=["user"],
)
