from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db

router = APIRouter()

@router.get('/dashboard')
def dashboard(db: Session = Depends(get_db)) -> dict:
    summary = db.execute(text("""
        SELECT
          (SELECT count(*) FROM master.product) products,
          (SELECT count(*) FROM ops.order_header) orders,
          (SELECT count(*) FROM engine.cubication_run) runs,
          (SELECT count(*) FROM audit.source_import_log) imports
    """)).mappings().one()
    recent_imports = db.execute(text("SELECT import_log_id, file_name, status, row_count FROM audit.source_import_log ORDER BY import_log_id DESC LIMIT 5")).mappings().all()
    recent_runs = db.execute(text("""
        SELECT r.run_id, oh.order_no, cr.recommendation_status
        FROM engine.cubication_run r
        LEFT JOIN engine.cubication_result cr ON cr.run_id = r.run_id
        LEFT JOIN ops.order_header oh ON oh.order_id = r.order_id
        ORDER BY r.run_id DESC LIMIT 5
    """)).mappings().all()
    breakdown = db.execute(text("""
        SELECT COALESCE(recommendation_status, 'manual_review') recommendation_status, count(*)
        FROM engine.cubication_result GROUP BY recommendation_status ORDER BY count(*) DESC
    """)).mappings().all()
    return {"summary": dict(summary), "recentImports": [dict(r) for r in recent_imports], "recentRuns": [dict(r) for r in recent_runs], "recommendationBreakdown": [dict(r) for r in breakdown]}


def _list(db: Session, sql: str) -> list[dict]:
    return [dict(r) for r in db.execute(text(sql)).mappings().all()]

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
      SELECT oh.order_id, oh.order_no, c.customer_name, oh.status, oh.source_order_type, oh.source_reference_no
      FROM ops.order_header oh LEFT JOIN master.customer c ON c.customer_id=oh.customer_id WHERE oh.order_id=:id
    """), {"id": order_id}).mappings().first()
    if not header:
      raise HTTPException(404, 'Order not found')
    items = _list(db, f"""
      SELECT oi.order_item_id, oi.line_no, p.sku_code, p.product_name,
             oi.normalized_shipping_pack_qty AS sap_shipping_qty,
             oi.qty AS base_qty, oi.qty_uom, oi.gross_weight_total_kg, oi.volume_total_m3,
             sr.rule_code AS stacking_rule_code, sr.max_stack_layer
      FROM ops.order_item oi
      LEFT JOIN master.product p ON p.product_id=oi.product_id
      LEFT JOIN master.product_stacking_map psm ON psm.product_id=p.product_id
      LEFT JOIN master.stacking_rule sr ON sr.stacking_rule_id=psm.stacking_rule_id
      WHERE oi.order_id={order_id} ORDER BY oi.line_no
    """)
    summary = db.execute(text("SELECT coalesce(sum(gross_weight_total_kg),0) total_weight_kg, coalesce(sum(volume_total_m3),0) total_volume_m3, count(*) item_count FROM ops.order_item WHERE order_id=:id"), {"id": order_id}).mappings().one()
    return {"header": dict(header), "items": items, "summary": dict(summary)}

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
    run_items = _list(db, f"""
      SELECT ri.run_item_id, p.sku_code, p.product_name, ri.qty_shipping_pack, ri.total_weight_kg, ri.total_volume_m3, ri.max_stack_layer, ri.stack_layers_used
      FROM engine.cubication_run_item ri LEFT JOIN master.product p ON p.product_id=ri.product_id
      WHERE ri.run_id={run_id} ORDER BY ri.run_item_id
    """)
    candidates = _list(db, f"""
      SELECT c.candidate_id, t.truck_name, t.max_payload_kg, t.cargo_volume_m3, c.weight_utilization_pct, c.volume_utilization_pct,
      c.pass_weight, c.pass_volume, c.pass_floor_area, c.pass_height, c.rank_no, c.rejection_reason
      FROM engine.cubication_candidate c LEFT JOIN master.truck_type t ON t.truck_type_id = c.truck_type_id
      WHERE c.run_id={run_id} ORDER BY c.rank_no NULLS LAST, c.candidate_id
    """)
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
    return _list(db, f'SELECT validation_error_id, row_identifier, field_name, error_code, error_message, severity FROM audit.validation_error WHERE import_log_id={log_id} ORDER BY validation_error_id')

@router.post('/imports/{import_type}')
async def upload(import_type: str, file: UploadFile = File(...), db: Session = Depends(get_db)) -> dict:
    row = db.execute(text("""
      INSERT INTO audit.source_import_log (source_name, file_name, import_type, status, notes, started_at, finished_at)
      VALUES ('frontend_upload', :file_name, :import_type, 'uploaded', 'Uploaded via Stage 5 UI (processing not implemented yet)', now(), now())
      RETURNING import_log_id
    """), {"file_name": file.filename, "import_type": import_type}).mappings().one()
    db.commit()
    return {"ok": True, "import_log_id": row['import_log_id']}
