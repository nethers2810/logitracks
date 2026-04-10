from fastapi import FastAPI

from app.api.imports import router as import_router

app = FastAPI(title="Logitracks Import API")
app.include_router(import_router)
