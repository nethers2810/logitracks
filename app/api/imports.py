from __future__ import annotations

from fastapi import APIRouter, File, UploadFile
from sqlalchemy import text

from app.db import get_session
from app.importers.master_importers import (
    import_customers,
    import_products,
    import_trucks,
    import_vendor_allocations,
)
from app.importers.sap_importer import import_sap_deliveries

router = APIRouter(prefix="/api/imports", tags=["imports"])


@router.post("/products")
async def upload_products(file: UploadFile = File(...)) -> dict:
    with get_session() as session:
        result = import_products(session, file.filename or "products.xlsx", await file.read())
        return result.__dict__


@router.post("/customers")
async def upload_customers(file: UploadFile = File(...)) -> dict:
    with get_session() as session:
        result = import_customers(session, file.filename or "customers.xlsx", await file.read())
        return result.__dict__


@router.post("/trucks")
async def upload_trucks(file: UploadFile = File(...)) -> dict:
    with get_session() as session:
        result = import_trucks(session, file.filename or "trucks.xlsx", await file.read())
        return result.__dict__


@router.post("/vendor-allocation")
async def upload_vendor_allocations(file: UploadFile = File(...)) -> dict:
    with get_session() as session:
        result = import_vendor_allocations(session, file.filename or "vendor_allocation.xlsx", await file.read())
        return result.__dict__


@router.post("/sap-deliveries")
async def upload_sap_deliveries(file: UploadFile = File(...)) -> dict:
    with get_session() as session:
        result = import_sap_deliveries(session, file.filename or "sap_deliveries.xlsx", await file.read())
        return result.__dict__


@router.get("/logs")
def list_import_logs(limit: int = 100) -> list[dict]:
    with get_session() as session:
        rows = session.execute(
            text(
                """
                SELECT source_import_log_id, source_type, file_name, status, row_count, processed_rows, error_rows, started_at, finished_at
                FROM audit.source_import_log
                ORDER BY source_import_log_id DESC
                LIMIT :limit
                """
            ),
            {"limit": limit},
        ).mappings()
        return [dict(r) for r in rows]


@router.get("/logs/{log_id}/errors")
def list_import_errors(log_id: int, limit: int = 500) -> list[dict]:
    with get_session() as session:
        rows = session.execute(
            text(
                """
                SELECT validation_error_id, row_number, field_name, error_code, error_message, raw_payload, created_at
                FROM audit.validation_error
                WHERE source_import_log_id = :log_id
                ORDER BY validation_error_id ASC
                LIMIT :limit
                """
            ),
            {"log_id": log_id, "limit": limit},
        ).mappings()
        return [dict(r) for r in rows]
