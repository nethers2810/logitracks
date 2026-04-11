import csv
import io
import json
from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_roles
from app.core.exceptions import AppError
from app.db.models.audit import SourceImportLog, ValidationError
from app.db.models.master import Customer, Product, TruckType, VendorLaneAllocation
from app.db.models.ops import OrderHeader, OrderItem
from app.services.cubication_engine import run_order_simulation

router = APIRouter(dependencies=[Depends(require_roles("admin", "planner", "analyst"))])


def _list(db: Session, sql: str, params: dict | None = None) -> list[dict]:
    return [dict(r) for r in db.execute(text(sql), params or {}).mappings().all()]


@router.get('/dashboard')
def dashboard(db: Session = Depends(get_db)) -> dict:
    summary = db.execute(text("""
        SELECT
          (SELECT count(*) FROM master.product) products,
          (SELECT count(*) FROM ops.order_header) orders,
          (SELECT count(*) FROM engine.cubication_run) runs,
          (SELECT count(*) FROM audit.source_import_log) imports
    """)).mappings().one()
    return {
        "summary": dict(summary),
        "recentImports": _list(db, "SELECT import_log_id, file_name, status, row_count FROM audit.source_import_log ORDER BY import_log_id DESC LIMIT 5"),
        "recentRuns": _list(db, """
            SELECT r.run_id, oh.order_no, cr.recommendation_status
            FROM engine.cubication_run r
            LEFT JOIN engine.cubication_result cr ON cr.run_id = r.run_id
            LEFT JOIN ops.order_header oh ON oh.order_id = r.order_id
            ORDER BY r.run_id DESC LIMIT 5
        """),
        "recommendationBreakdown": _list(db, """
            SELECT COALESCE(recommendation_status, 'manual_review') recommendation_status, count(*)
            FROM engine.cubication_result GROUP BY recommendation_status ORDER BY count(*) DESC
        """),
    }


@router.get('/products')
def products(db: Session = Depends(get_db)) -> list[dict]:
    return _list(db, "SELECT product_id, sku_code, product_name, category_name, subcategory_name, base_uom, gross_weight_kg, volume_m3 FROM master.product ORDER BY product_id DESC LIMIT 500")


@router.get('/truck-types')
def truck_types(db: Session = Depends(get_db)) -> list[dict]:
    return _list(db, "SELECT truck_type_id, truck_code, truck_name, max_payload_kg, cargo_volume_m3, truck_group FROM master.truck_type ORDER BY truck_type_id DESC")


@router.get('/stacking-rules')
def stacking_rules(db: Session = Depends(get_db)) -> list[dict]:
    return _list(db, "SELECT stacking_rule_id, rule_code, category_name, subcategory_name, max_stack_layer, is_active FROM master.stacking_rule ORDER BY stacking_rule_id DESC")


@router.get('/customers')
def customers(db: Session = Depends(get_db)) -> list[dict]:
    return _list(db, "SELECT customer_id, customer_code, customer_name, city, zone, region FROM master.customer ORDER BY customer_id DESC")


@router.get('/vendor-allocations')
def vendor_allocations(db: Session = Depends(get_db)) -> list[dict]:
    return _list(db, """
      SELECT v.vendor_lane_allocation_id, v.customer_code, v.ship_to_code, v.route_code, t.truck_name, v.priority_no, v.is_active
      FROM master.vendor_lane_allocation v
      LEFT JOIN master.truck_type t ON t.truck_type_id = v.truck_type_id
      ORDER BY v.vendor_lane_allocation_id DESC
    """)


@router.get('/orders')
def orders(db: Session = Depends(get_db)) -> list[dict]:
    return _list(db, """
      SELECT oh.order_id, oh.order_no, c.customer_name, oh.planned_delivery_date, oh.status,
             count(oi.order_item_id) line_count, coalesce(sum(oi.gross_weight_total_kg),0) total_weight_kg, coalesce(sum(oi.volume_total_m3),0) total_volume_m3
      FROM ops.order_header oh
      LEFT JOIN master.customer c ON c.customer_id=oh.customer_id
      LEFT JOIN ops.order_item oi ON oi.order_id=oh.order_id
      GROUP BY oh.order_id, c.customer_name
      ORDER BY oh.order_id DESC
    """)


@router.get('/orders/{order_id}')
def order_detail(order_id: int, db: Session = Depends(get_db)) -> dict:
    header = db.execute(text("""
      SELECT oh.order_id, oh.order_no, c.customer_name, oh.status, oh.source_order_type, oh.source_reference_no,
             (SELECT r.run_id FROM engine.cubication_run r WHERE r.order_id=oh.order_id ORDER BY r.run_id DESC LIMIT 1) AS latest_run_id
      FROM ops.order_header oh LEFT JOIN master.customer c ON c.customer_id=oh.customer_id WHERE oh.order_id=:id
    """), {"id": order_id}).mappings().first()
    if not header:
      raise HTTPException(404, 'Order not found')
    items = _list(db, """
      SELECT oi.order_item_id, oi.line_no, p.sku_code, p.product_name,
             oi.normalized_shipping_pack_qty AS sap_shipping_qty,
             oi.qty AS base_qty, oi.qty_uom, oi.gross_weight_total_kg, oi.volume_total_m3,
             sr.rule_code AS stacking_rule_code, sr.max_stack_layer
      FROM ops.order_item oi
      LEFT JOIN master.product p ON p.product_id=oi.product_id
      LEFT JOIN master.product_stacking_map psm ON psm.product_id=p.product_id
      LEFT JOIN master.stacking_rule sr ON sr.stacking_rule_id=psm.stacking_rule_id
      WHERE oi.order_id=:order_id ORDER BY oi.line_no
    """, {"order_id": order_id})
    summary = db.execute(text("SELECT coalesce(sum(gross_weight_total_kg),0) total_weight_kg, coalesce(sum(volume_total_m3),0) total_volume_m3, count(*) item_count FROM ops.order_item WHERE order_id=:id"), {"id": order_id}).mappings().one()
    return {"header": dict(header), "items": items, "summary": dict(summary)}


@router.post('/orders/{order_id}/simulate')
def simulate_order(order_id: int, db: Session = Depends(get_db)) -> dict:
    run = run_order_simulation(db, order_id)
    return {"ok": True, "run_id": run.run_id}


@router.get('/simulation-runs/{run_id}')
def simulation(run_id: int, db: Session = Depends(get_db)) -> dict:
    header = db.execute(text("""
      SELECT r.run_id, r.order_id, r.status, r.algorithm_version, r.created_at,
             cr.recommendation_status, cr.recommendation_reason, cr.result_json
      FROM engine.cubication_run r
      LEFT JOIN engine.cubication_result cr ON cr.run_id=r.run_id
      WHERE r.run_id=:id
    """), {"id": run_id}).mappings().first()
    if not header:
      raise HTTPException(404, 'Run not found')
    run_items = _list(db, """
      SELECT ri.run_item_id, p.sku_code, p.product_name, ri.qty_shipping_pack, ri.total_weight_kg, ri.total_volume_m3, ri.max_stack_layer, ri.stack_layers_used
      FROM engine.cubication_run_item ri LEFT JOIN master.product p ON p.product_id=ri.product_id
      WHERE ri.run_id=:run_id ORDER BY ri.run_item_id
    """, {"run_id": run_id})
    candidates = _list(db, """
      SELECT c.candidate_id, t.truck_name, t.max_payload_kg, t.cargo_volume_m3, c.weight_utilization_pct, c.volume_utilization_pct,
      c.pass_weight, c.pass_volume, c.pass_floor_area, c.pass_height, c.rank_no, c.rejection_reason
      FROM engine.cubication_candidate c LEFT JOIN master.truck_type t ON t.truck_type_id = c.truck_type_id
      WHERE c.run_id=:run_id ORDER BY c.rank_no NULLS LAST, c.candidate_id
    """, {"run_id": run_id})
    payload = dict(header)
    split = (payload.get('result_json') or {}).get('split_recommendation') if isinstance(payload.get('result_json'), dict) else None
    payload.pop('result_json', None)
    payload['run_items'] = run_items
    payload['candidates'] = candidates
    payload['split_recommendation'] = split
    return payload


@router.get('/imports/logs')
def import_logs(db: Session = Depends(get_db)) -> list[dict]:
    return _list(db, 'SELECT import_log_id, source_name, file_name, status, row_count, success_count, error_count, started_at, finished_at FROM audit.source_import_log ORDER BY import_log_id DESC LIMIT 100')


@router.get('/imports/logs/{log_id}/errors')
def import_errors(log_id: int, db: Session = Depends(get_db)) -> list[dict]:
    return _list(db, 'SELECT validation_error_id, row_identifier, field_name, error_code, error_message, severity FROM audit.validation_error WHERE import_log_id=:log_id ORDER BY validation_error_id', {"log_id": log_id})


def _create_log(db: Session, import_type: str, filename: str) -> SourceImportLog:
    log = SourceImportLog(source_name="frontend_upload", file_name=filename, import_type=import_type, status="processing")
    db.add(log)
    db.flush()
    return log


@router.post('/imports/{import_type}')
async def upload(import_type: str, file: UploadFile = File(...), db: Session = Depends(get_db)) -> dict:
    body = await file.read()
    content = body.decode("utf-8")
    log = _create_log(db, import_type, file.filename or "upload")
    rows = 0
    success = 0
    errors = 0
    try:
        if import_type == "products":
            for row in csv.DictReader(io.StringIO(content)):
                rows += 1
                if not row.get("sku_code"):
                    errors += 1
                    db.add(ValidationError(import_log_id=log.import_log_id, row_identifier=str(rows), field_name="sku_code", error_code="required", error_message="sku_code is required", severity="error"))
                    continue
                product = db.scalars(select(Product).where(Product.sku_code == row["sku_code"])).first()
                if not product:
                    product = Product(sku_code=row["sku_code"])
                    db.add(product)
                product.product_name = row.get("product_name")
                product.category_name = row.get("category_name")
                product.gross_weight_kg = Decimal(row["gross_weight_kg"]) if row.get("gross_weight_kg") else None
                product.volume_m3 = Decimal(row["volume_m3"]) if row.get("volume_m3") else None
                success += 1
        elif import_type == "customers":
            for row in csv.DictReader(io.StringIO(content)):
                rows += 1
                if not row.get("customer_code"):
                    errors += 1
                    continue
                customer = db.scalars(select(Customer).where(Customer.customer_code == row["customer_code"])).first() or Customer(customer_code=row["customer_code"])
                db.add(customer)
                customer.customer_name = row.get("customer_name")
                customer.city = row.get("city")
                customer.zone = row.get("zone")
                customer.region = row.get("region")
                success += 1
        elif import_type == "trucks":
            for row in csv.DictReader(io.StringIO(content)):
                rows += 1
                if not row.get("truck_code"):
                    errors += 1
                    continue
                truck = db.scalars(select(TruckType).where(TruckType.truck_code == row["truck_code"])).first() or TruckType(truck_code=row["truck_code"])
                db.add(truck)
                truck.truck_name = row.get("truck_name")
                truck.max_payload_kg = Decimal(row["max_payload_kg"]) if row.get("max_payload_kg") else None
                truck.cargo_volume_m3 = Decimal(row["cargo_volume_m3"]) if row.get("cargo_volume_m3") else None
                truck.truck_group = row.get("truck_group")
                success += 1
        elif import_type == "vendor-allocation":
            for row in csv.DictReader(io.StringIO(content)):
                rows += 1
                if not row.get("customer_code") or not row.get("truck_type_id"):
                    errors += 1
                    continue
                db.add(VendorLaneAllocation(customer_code=row.get("customer_code"), ship_to_code=row.get("ship_to_code"), route_code=row.get("route_code"), truck_type_id=int(row.get("truck_type_id")), priority_no=int(row.get("priority_no") or 1), is_active=True))
                success += 1
        elif import_type == "sap-deliveries":
            payload = json.loads(content)
            if isinstance(payload, dict):
                payload = [payload]
            for doc in payload:
                rows += 1
                customer = db.scalars(select(Customer).where(Customer.customer_code == doc.get("customer_code"))).first()
                if not customer:
                    errors += 1
                    db.add(ValidationError(import_log_id=log.import_log_id, row_identifier=str(rows), field_name="customer_code", error_code="not_found", error_message="Unknown customer_code", severity="error"))
                    continue
                order = OrderHeader(order_no=doc.get("order_no") or f"SAP-{date.today()}-{rows}", customer_id=customer.customer_id, source_order_type="SAP", source_reference_no=doc.get("source_reference_no"), planned_delivery_date=date.fromisoformat(doc.get("planned_delivery_date")) if doc.get("planned_delivery_date") else date.today(), status="imported")
                db.add(order)
                db.flush()
                for idx, item in enumerate(doc.get("items", []), start=1):
                    db.add(OrderItem(order_id=order.order_id, product_id=int(item["product_id"]), packaging_id=item.get("packaging_id"), line_no=idx, qty=Decimal(str(item.get("qty", 0))), qty_uom=item.get("qty_uom", "CASE"), normalized_shipping_pack_qty=Decimal(str(item.get("normalized_shipping_pack_qty", item.get("qty", 0)))), gross_weight_total_kg=Decimal(str(item.get("gross_weight_total_kg", 0))), volume_total_m3=Decimal(str(item.get("volume_total_m3", 0)))) )
                success += 1
        else:
            raise AppError("Unsupported import type", status_code=400, code="validation_error")

        log.status = "completed"
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    log.row_count = rows
    log.success_count = success
    log.error_count = errors
    log.status = "completed_with_errors" if errors else "completed"
    db.commit()
    return {"ok": True, "import_log_id": log.import_log_id, "row_count": rows, "success_count": success, "error_count": errors}
