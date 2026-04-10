from fastapi import APIRouter

from app.api.routers.health import router as health_router
from app.api.routers.data import router as data_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(data_router, tags=["data"])
