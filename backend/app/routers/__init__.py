from fastapi import APIRouter

from backend.app.routers.v1 import router as v1_router

api_router = APIRouter(prefix="/api")

api_router.include_router(
    router=v1_router,
    prefix="/v1",
)
