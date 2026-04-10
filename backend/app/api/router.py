from fastapi import APIRouter

from app.api.routers.dashboard import router as dashboard_router
from app.api.routers.health import router as health_router
from app.api.routers.master import router as master_router
from app.api.routers.orders import router as orders_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(master_router, tags=["master"])
api_router.include_router(orders_router, tags=["orders"])
api_router.include_router(dashboard_router, tags=["dashboard"])
