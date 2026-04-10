from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="LogiTracks backend API skeleton for cubication foundation.",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

register_exception_handlers(app)
app.include_router(api_router, prefix="/api")
