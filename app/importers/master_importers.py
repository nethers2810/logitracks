from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.importers.base import ImportResult, missing_required_columns, read_excel
from app.services.audit import AuditService


def import_products(session: Session, file_name: str, content: bytes) -> ImportResult:
    df = read_excel(content)
    required = {"material_code", "material_name"}
    audit = AuditService(session)
    ctx = audit.create_import_log("products", file_name, len(df))
    missing = missing_required_columns(df, required)
    if missing:
        for col in missing:
            audit.add_validation_error(ctx.source_import_log_id, None, col, "MISSING_COLUMN", f"Required column missing: {col}")
        audit.mark_complete(ctx.source_import_log_id, 0, len(missing))
        return ImportResult(0, len(missing))

    errors = 0
    processed = 0
    for i, row in df.iterrows():
        material_code = str(row.get("material_code", "")).strip()
        if not material_code:
            errors += 1
            audit.add_validation_error(ctx.source_import_log_id, i + 2, "material_code", "REQUIRED", "material_code is required", row.to_dict())
            continue
        session.execute(
            text(
                """
                INSERT INTO master.product (material_code, material_name, category, subcategory, pack_size_label, base_uom, updated_at)
                VALUES (:material_code, :material_name, :category, :subcategory, :pack_size_label, :base_uom, now())
                ON CONFLICT (material_code)
                DO UPDATE SET
                    material_name = EXCLUDED.material_name,
                    category = COALESCE(EXCLUDED.category, master.product.category),
                    subcategory = COALESCE(EXCLUDED.subcategory, master.product.subcategory),
                    pack_size_label = COALESCE(EXCLUDED.pack_size_label, master.product.pack_size_label),
                    base_uom = COALESCE(EXCLUDED.base_uom, master.product.base_uom),
                    updated_at = now()
                """
            ),
            row.to_dict(),
        )
        processed += 1
    audit.mark_complete(ctx.source_import_log_id, processed, errors)
    return ImportResult(processed, errors)


def import_customers(session: Session, file_name: str, content: bytes) -> ImportResult:
    return _generic_import(
        session,
        file_name,
        content,
        "customers",
        {"customer_code", "customer_name"},
        """
        INSERT INTO master.customer (customer_code, customer_name, ship_to_code, city, zone, region, updated_at)
        VALUES (:customer_code, :customer_name, :ship_to_code, :city, :zone, :region, now())
        ON CONFLICT (customer_code) DO UPDATE SET
          customer_name=EXCLUDED.customer_name,
          ship_to_code=COALESCE(EXCLUDED.ship_to_code, master.customer.ship_to_code),
          city=COALESCE(EXCLUDED.city, master.customer.city),
          zone=COALESCE(EXCLUDED.zone, master.customer.zone),
          region=COALESCE(EXCLUDED.region, master.customer.region),
          updated_at=now()
        """,
        "customer_code",
    )


def import_trucks(session: Session, file_name: str, content: bytes) -> ImportResult:
    return _generic_import(
        session,
        file_name,
        content,
        "trucks",
        {"truck_code", "truck_name"},
        """
        INSERT INTO master.truck_type (truck_code, truck_name, capacity_weight_kg, capacity_volume_m3, updated_at)
        VALUES (:truck_code, :truck_name, :capacity_weight_kg, :capacity_volume_m3, now())
        ON CONFLICT (truck_code) DO UPDATE SET
          truck_name=EXCLUDED.truck_name,
          capacity_weight_kg=COALESCE(EXCLUDED.capacity_weight_kg, master.truck_type.capacity_weight_kg),
          capacity_volume_m3=COALESCE(EXCLUDED.capacity_volume_m3, master.truck_type.capacity_volume_m3),
          updated_at=now()
        """,
        "truck_code",
    )


def import_vendor_allocations(session: Session, file_name: str, content: bytes) -> ImportResult:
    return _generic_import(
        session,
        file_name,
        content,
        "vendor_allocation",
        {"truck_code", "priority_no"},
        """
        INSERT INTO master.vendor_lane_allocation
            (ship_to_code, customer_code, city, zone, region, route_code, truck_type_id, priority_no, is_active, notes, created_at, updated_at)
        VALUES
            (:ship_to_code, :customer_code, :city, :zone, :region, :route_code,
             (SELECT truck_type_id FROM master.truck_type WHERE truck_code = :truck_code),
             :priority_no, COALESCE(:is_active, true), :notes, now(), now())
        ON CONFLICT DO NOTHING
        """,
        "truck_code",
    )


def _generic_import(session: Session, file_name: str, content: bytes, source_type: str, required: set[str], sql: str, key_col: str) -> ImportResult:
    df = read_excel(content)
    audit = AuditService(session)
    ctx = audit.create_import_log(source_type, file_name, len(df))
    missing = missing_required_columns(df, required)
    if missing:
        for col in missing:
            audit.add_validation_error(ctx.source_import_log_id, None, col, "MISSING_COLUMN", f"Required column missing: {col}")
        audit.mark_complete(ctx.source_import_log_id, 0, len(missing))
        return ImportResult(0, len(missing))

    errors = 0
    processed = 0
    for i, row in df.iterrows():
        if not str(row.get(key_col, "")).strip():
            errors += 1
            audit.add_validation_error(ctx.source_import_log_id, i + 2, key_col, "REQUIRED", f"{key_col} is required", row.to_dict())
            continue
        session.execute(text(sql), row.to_dict())
        processed += 1
    audit.mark_complete(ctx.source_import_log_id, processed, errors)
    return ImportResult(processed, errors)
