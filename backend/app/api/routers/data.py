from datetime import UTC, datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.models.engine import CubicationCandidate, CubicationResult, CubicationRun, CubicationRunItem
from app.db.session import get_db



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
    recent_imports = db.execute(text('SELECT import_log_id, file_name, status, row_count FROM audit.source_import_log ORDER BY import_log_id DESC LIMIT 5')).mappings().all()
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
    return {
        'summary': dict(summary),
        'recentImports': [dict(r) for r in recent_imports],
        'recentRuns': [dict(r) for r in recent_runs],
        'recommendationBreakdown': [dict(r) for r in breakdown],
    }


@router.get('/products')
def products(db: Session = Depends(get_db)) -> list[dict]:
    return _list(db, 'SELECT product_id, sku_code, product_name, category_name, subcategory_name, base_uom, gross_weight_kg, volume_m3 FROM master.product ORDER BY product_id DESC LIMIT 500')



@router.get('/truck-types')
def truck_types(db: Session = Depends(get_db)) -> list[dict]:
    return _list(db, 'SELECT truck_type_id, truck_code, truck_name, max_payload_kg, cargo_volume_m3, truck_group FROM master.truck_type ORDER BY truck_type_id DESC')



@router.get('/stacking-rules')
def stacking_rules(db: Session = Depends(get_db)) -> list[dict]:
    return _list(db, 'SELECT stacking_rule_id, rule_code, category_name, subcategory_name, max_stack_layer, is_active FROM master.stacking_rule ORDER BY stacking_rule_id DESC')



@router.get('/customers')
def customers(db: Session = Depends(get_db)) -> list[dict]:
    return _list(db, 'SELECT customer_id, customer_code, customer_name, city, zone, region FROM master.customer ORDER BY customer_id DESC')



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
    """), {'id': order_id}).mappings().first()
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
      WHERE oi.order_id=:id ORDER BY oi.line_no
    """, {'id': order_id})
    summary = db.execute(text('SELECT coalesce(sum(gross_weight_total_kg),0) total_weight_kg, coalesce(sum(volume_total_m3),0) total_volume_m3, count(*) item_count FROM ops.order_item WHERE order_id=:id'), {'id': order_id}).mappings().one()
    latest_run = db.execute(text('SELECT run_id FROM engine.cubication_run WHERE order_id=:id ORDER BY run_id DESC LIMIT 1'), {'id': order_id}).scalar_one_or_none()
    return {'header': dict(header), 'items': items, 'summary': dict(summary), 'latest_run_id': latest_run}


@router.get('/orders/{order_id}/latest-run')
def latest_run(order_id: int, db: Session = Depends(get_db)) -> dict:
    run_id = db.execute(text('SELECT run_id FROM engine.cubication_run WHERE order_id=:id ORDER BY run_id DESC LIMIT 1'), {'id': order_id}).scalar_one_or_none()
    return {'order_id': order_id, 'run_id': run_id}


@router.post('/orders/{order_id}/simulate')
def run_simulation(order_id: int, db: Session = Depends(get_db)) -> dict:
    order = db.execute(text('SELECT order_id FROM ops.order_header WHERE order_id=:id'), {'id': order_id}).mappings().first()
    if not order:
        raise HTTPException(404, 'Order not found')

    item_rows = _list(db, """
        SELECT oi.order_item_id, oi.product_id, oi.packaging_id, oi.qty,
               COALESCE(oi.gross_weight_total_kg, 0) gross_weight_total_kg,
               COALESCE(oi.volume_total_m3, 0) volume_total_m3,
               COALESCE(pp.length_mm, 0) length_mm,
               COALESCE(pp.width_mm, 0) width_mm,
               COALESCE(pp.height_mm, 0) height_mm,
               COALESCE(pp.gross_weight_per_pack_kg, 0) gross_weight_per_pack_kg,
               COALESCE(pp.case_volume_m3, 0) case_volume_m3,
               COALESCE(sr.max_stack_layer, 1) max_stack_layer
        FROM ops.order_item oi
        LEFT JOIN master.product_packaging pp ON pp.packaging_id = oi.packaging_id
        LEFT JOIN master.product_stacking_map psm ON psm.product_id = oi.product_id
        LEFT JOIN master.stacking_rule sr ON sr.stacking_rule_id = psm.stacking_rule_id
        WHERE oi.order_id = :id
        ORDER BY oi.line_no
    """, {'id': order_id})

    if not item_rows:
        raise HTTPException(422, 'Order has no items')

    total_weight = sum(Decimal(str(r['gross_weight_total_kg'])) for r in item_rows)
    total_volume = sum(Decimal(str(r['volume_total_m3'])) for r in item_rows)
    total_floor = sum((Decimal(str(r['length_mm'])) / Decimal('1000')) * (Decimal(str(r['width_mm'])) / Decimal('1000')) * Decimal(str(r['qty'] or 0)) / max(Decimal(str(r['max_stack_layer'] or 1)), Decimal('1')) for r in item_rows)

    run = CubicationRun(
        order_id=order_id,
        algorithm_version='pilot-v1',
        calculation_mode='stacked',
        status='completed',
        run_started_at=datetime.now(UTC),
        run_finished_at=datetime.now(UTC),
        odol_safety_factor=Decimal('0.95'),
        floor_utilization_limit_pct=Decimal('98'),
        volume_utilization_limit_pct=Decimal('98'),
        weight_utilization_limit_pct=Decimal('95'),
    )
    db.add(run)
    db.flush()

    for r in item_rows:
        qty = Decimal(str(r['qty'] or 0))
        max_stack_layer = int(r['max_stack_layer'] or 1)
        stack_layers_used = min(max_stack_layer, int(qty) if qty > 0 else 1)
        stack_count = int((qty / Decimal(max(max_stack_layer, 1))).to_integral_value(rounding='ROUND_CEILING')) if qty > 0 else 0
        db.add(CubicationRunItem(
            run_id=run.run_id,
            order_item_id=r['order_item_id'],
            product_id=r['product_id'],
            packaging_id=r['packaging_id'],
            qty_shipping_pack=qty,
            gross_weight_per_pack_kg=Decimal(str(r['gross_weight_per_pack_kg'])),
            total_weight_kg=Decimal(str(r['gross_weight_total_kg'])),
            length_mm=Decimal(str(r['length_mm'])),
            width_mm=Decimal(str(r['width_mm'])),
            height_mm=Decimal(str(r['height_mm'])),
            case_volume_m3=Decimal(str(r['case_volume_m3'])),
            total_volume_m3=Decimal(str(r['volume_total_m3'])),
            max_stack_layer=max_stack_layer,
            stack_layers_used=stack_layers_used,
            stack_count=stack_count,
            required_floor_area_m2=((Decimal(str(r['length_mm'])) / Decimal('1000')) * (Decimal(str(r['width_mm'])) / Decimal('1000')) * qty / max(Decimal(max_stack_layer), Decimal('1'))),
            required_height_mm=Decimal(str(r['height_mm'])) * min(Decimal(max_stack_layer), qty if qty > 0 else Decimal('1')),
        ))

    truck_rows = _list(db, """
        SELECT DISTINCT tt.truck_type_id, tt.truck_name, tt.max_payload_kg, tt.cargo_volume_m3, tt.deck_area_m2
        FROM ops.order_header oh
        LEFT JOIN master.customer c ON c.customer_id = oh.customer_id
        LEFT JOIN master.vendor_lane_allocation vla ON vla.customer_code = c.customer_code AND vla.is_active IS TRUE
        LEFT JOIN master.truck_type tt ON tt.truck_type_id = vla.truck_type_id
        WHERE oh.order_id = :id
        ORDER BY tt.truck_type_id
    """, {'id': order_id})
    if not truck_rows:
        truck_rows = _list(db, 'SELECT truck_type_id, truck_name, max_payload_kg, cargo_volume_m3, deck_area_m2 FROM master.truck_type ORDER BY truck_type_id LIMIT 5')

    winner: CubicationCandidate | None = None
    for idx, t in enumerate(truck_rows, start=1):
        if not t['truck_type_id']:
            continue
        payload = Decimal(str(t['max_payload_kg'] or 0))
        capacity_volume = Decimal(str(t['cargo_volume_m3'] or 0))
        deck_area = Decimal(str(t['deck_area_m2'] or 0))

        pass_weight = total_weight <= payload * Decimal('0.95') if payload > 0 else False
        pass_volume = total_volume <= capacity_volume if capacity_volume > 0 else False
        pass_floor = total_floor <= deck_area if deck_area > 0 else False
        pass_height = True
        full_pass = pass_weight and pass_volume and pass_floor and pass_height
        score = ((total_weight / payload) * Decimal('100') + (total_volume / capacity_volume) * Decimal('100')) / Decimal('2') if full_pass and payload > 0 and capacity_volume > 0 else None

        candidate = CubicationCandidate(
            run_id=run.run_id,
            truck_type_id=t['truck_type_id'],
            total_weight_kg=total_weight,
            total_volume_m3=total_volume,
            total_required_floor_area_m2=total_floor,
            pass_weight=pass_weight,
            pass_volume=pass_volume,
            pass_floor_area=pass_floor,
            pass_height=pass_height,
            pass_customer_constraint=True,
            weight_utilization_pct=(total_weight / payload) * Decimal('100') if payload > 0 else None,
            volume_utilization_pct=(total_volume / capacity_volume) * Decimal('100') if capacity_volume > 0 else None,
            floor_utilization_pct=(total_floor / deck_area) * Decimal('100') if deck_area > 0 else None,
            score=score,
            rank_no=idx if full_pass else None,
            rejection_reason=None if full_pass else 'Failed one or more capacity checks',
        )
        db.add(candidate)
        if full_pass and (winner is None or (candidate.score or Decimal('9999')) < (winner.score or Decimal('9999'))):
            winner = candidate

    status = 'success' if winner else 'manual_review'
    reason = 'Recommended best-fit truck from lane allocation and payload checks' if winner else 'No truck passed all constraints; planner review required'

    db.add(CubicationResult(
        run_id=run.run_id,
        recommended_truck_type_id=winner.truck_type_id if winner else None,
        recommendation_status=status,
        total_weight_kg=total_weight,
        total_volume_m3=total_volume,
        total_required_floor_area_m2=total_floor,
        total_stack_count=sum(int(r['qty'] or 0) for r in item_rows),
        recommendation_reason=reason,
        result_json={'generated_by': 'pilot_simulation', 'order_id': order_id},
    ))
    db.commit()

    return {'ok': True, 'run_id': run.run_id, 'order_id': order_id, 'recommendation_status': status}



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
    """), {'id': run_id}).mappings().first()
    if not header:
        raise HTTPException(404, 'Run not found')
    run_items = _list(db, """
      SELECT ri.run_item_id, p.sku_code, p.product_name, ri.qty_shipping_pack, ri.total_weight_kg, ri.total_volume_m3, ri.max_stack_layer, ri.stack_layers_used
      FROM engine.cubication_run_item ri LEFT JOIN master.product p ON p.product_id=ri.product_id
      WHERE ri.run_id=:id ORDER BY ri.run_item_id
    """, {'id': run_id})
    candidates = _list(db, """
      SELECT c.candidate_id, t.truck_name, t.max_payload_kg, t.cargo_volume_m3, c.weight_utilization_pct, c.volume_utilization_pct,
      c.pass_weight, c.pass_volume, c.pass_floor_area, c.pass_height, c.rank_no, c.rejection_reason
      FROM engine.cubication_candidate c LEFT JOIN master.truck_type t ON t.truck_type_id = c.truck_type_id
      WHERE c.run_id=:id ORDER BY c.rank_no NULLS LAST, c.candidate_id
    """, {'id': run_id})
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
    return _list(db, 'SELECT validation_error_id, row_identifier, field_name, error_code, error_message, severity FROM audit.validation_error WHERE import_log_id=:id ORDER BY validation_error_id', {'id': log_id})


@router.post('/imports/{import_type}')
async def upload(import_type: str, file: UploadFile = File(...), db: Session = Depends(get_db)) -> dict:
    row = db.execute(text("""
      INSERT INTO audit.source_import_log (source_name, file_name, import_type, status, notes, started_at, finished_at)
      VALUES ('frontend_upload', :file_name, :import_type, 'uploaded', 'Uploaded via pilot UI', now(), now())
      RETURNING import_log_id
    """), {'file_name': file.filename, 'import_type': import_type}).mappings().one()
    db.commit()
    return {'ok': True, 'import_log_id': row['import_log_id']}
