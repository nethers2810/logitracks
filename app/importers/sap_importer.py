from __future__ import annotations

from collections import defaultdict

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.importers.base import ImportResult, missing_required_columns, read_excel
from app.services.audit import AuditService


REQUIRED_COLUMNS = {
    "delivery_no",
    "line_seq",
    "material_code",
    "delivery_qty",
    "delivery_uom",
    "actual_qty",
    "base_uom",
}


def import_sap_deliveries(session: Session, file_name: str, content: bytes) -> ImportResult:
    df = read_excel(content)
    audit = AuditService(session)
    ctx = audit.create_import_log("sap_deliveries", file_name, len(df))
    missing = missing_required_columns(df, REQUIRED_COLUMNS)
    if missing:
        for col in missing:
            audit.add_validation_error(ctx.source_import_log_id, None, col, "MISSING_COLUMN", f"Required column missing: {col}")
        audit.mark_complete(ctx.source_import_log_id, 0, len(missing))
        return ImportResult(0, len(missing))

    errors = 0
    processed = 0
    header_ids: dict[str, int] = {}
    for delivery_no, group in df.groupby("delivery_no"):
        h = group.iloc[0].to_dict()
        row = session.execute(
            text(
                """
                INSERT INTO ops.order_header
                    (source_system, source_delivery_no, customer_code, ship_to_code, route_code, planned_date, created_at, updated_at)
                VALUES
                    ('SAP', :delivery_no, :customer_code, :ship_to_code, :route_code, :planned_date, now(), now())
                ON CONFLICT (source_system, source_delivery_no)
                DO UPDATE SET
                    customer_code = COALESCE(EXCLUDED.customer_code, ops.order_header.customer_code),
                    ship_to_code = COALESCE(EXCLUDED.ship_to_code, ops.order_header.ship_to_code),
                    route_code = COALESCE(EXCLUDED.route_code, ops.order_header.route_code),
                    planned_date = COALESCE(EXCLUDED.planned_date, ops.order_header.planned_date),
                    updated_at = now()
                RETURNING order_header_id
                """
            ),
            h,
        ).one()
        header_ids[str(delivery_no)] = row[0]

    for i, row in df.iterrows():
        d = row.to_dict()
        delivery_qty = _to_float(d.get("delivery_qty"))
        actual_qty = _to_float(d.get("actual_qty"))
        if delivery_qty is None or actual_qty is None:
            errors += 1
            audit.add_validation_error(ctx.source_import_log_id, i + 2, "delivery_qty", "INVALID_NUMBER", "delivery_qty/actual_qty must be numeric", d)
            continue
        conversion = actual_qty / delivery_qty if delivery_qty else None

        session.execute(
            text(
                """
                INSERT INTO ops.order_item
                    (order_header_id, line_seq, material_code,
                     sap_delivery_qty, sap_delivery_uom, sap_actual_qty, sap_base_uom, conversion_factor,
                     sap_total_weight_kg, sap_total_volume_m3, sap_route, sap_product_type, sap_br, sap_region, sap_channel,
                     created_at, updated_at)
                VALUES
                    (:order_header_id, :line_seq, :material_code,
                     :delivery_qty, :delivery_uom, :actual_qty, :base_uom, :conversion_factor,
                     :total_weight_kg, :total_volume_m3, :route_code, :sap_product_type, :sap_br, :sap_region, :sap_channel,
                     now(), now())
                ON CONFLICT (order_header_id, line_seq, material_code)
                DO UPDATE SET
                     sap_delivery_qty = EXCLUDED.sap_delivery_qty,
                     sap_delivery_uom = EXCLUDED.sap_delivery_uom,
                     sap_actual_qty = EXCLUDED.sap_actual_qty,
                     sap_base_uom = EXCLUDED.sap_base_uom,
                     conversion_factor = EXCLUDED.conversion_factor,
                     sap_total_weight_kg = EXCLUDED.sap_total_weight_kg,
                     sap_total_volume_m3 = EXCLUDED.sap_total_volume_m3,
                     sap_route = EXCLUDED.sap_route,
                     sap_product_type = EXCLUDED.sap_product_type,
                     sap_br = EXCLUDED.sap_br,
                     sap_region = EXCLUDED.sap_region,
                     sap_channel = EXCLUDED.sap_channel,
                     updated_at = now()
                """
            ),
            {
                **d,
                "order_header_id": header_ids[str(d["delivery_no"])],
                "conversion_factor": conversion,
            },
        )
        processed += 1

    audit.mark_complete(ctx.source_import_log_id, processed, errors)
    return ImportResult(processed, errors)


def _to_float(v: object) -> float | None:
    try:
        if v is None:
            return None
        return float(v)
    except Exception:
        return None
