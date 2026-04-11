from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from math import ceil

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.db.models.engine import CubicationCandidate, CubicationResult, CubicationRun, CubicationRunItem
from app.db.models.master import Customer, CustomerDeliveryConstraint, Product, ProductPackaging, ProductStackingMap, StackingRule, TruckType, VendorLaneAllocation
from app.db.models.ops import OrderHeader, OrderItem


@dataclass
class AggregatedLoad:
    total_weight_kg: Decimal
    total_volume_m3: Decimal
    total_required_floor_area_m2: Decimal
    required_height_mm: Decimal
    total_stack_count: int


def _d(value: Decimal | float | int | None) -> Decimal:
    return Decimal(str(value or 0))


def run_order_simulation(db: Session, order_id: int) -> CubicationRun:
    order = db.get(OrderHeader, order_id)
    if not order:
        raise AppError("Order not found", status_code=404, code="not_found")

    customer = db.get(Customer, order.customer_id)
    customer_constraint = db.scalars(select(CustomerDeliveryConstraint).where(CustomerDeliveryConstraint.customer_id == order.customer_id)).first()

    rows = db.execute(
        select(OrderItem, Product, ProductPackaging)
        .join(Product, Product.product_id == OrderItem.product_id)
        .outerjoin(ProductPackaging, ProductPackaging.packaging_id == OrderItem.packaging_id)
        .where(OrderItem.order_id == order_id)
        .order_by(OrderItem.line_no)
    ).all()
    if not rows:
        raise AppError("Order has no items", status_code=422, code="validation_error")

    run = CubicationRun(
        order_id=order_id,
        algorithm_version="stage6-db-v1",
        calculation_mode="stacked",
        odol_safety_factor=Decimal("0.95"),
        status="running",
        run_started_at=datetime.now(UTC),
    )
    db.add(run)
    db.flush()

    aggregated = AggregatedLoad(Decimal("0"), Decimal("0"), Decimal("0"), Decimal("0"), 0)

    for oi, product, packaging in rows:
        mapping = db.scalars(
            select(ProductStackingMap)
            .where(ProductStackingMap.product_id == oi.product_id)
            .where((ProductStackingMap.packaging_id == oi.packaging_id) | (ProductStackingMap.packaging_id.is_(None)))
            .order_by(ProductStackingMap.packaging_id.desc().nulls_last())
        ).first()
        stack_rule = db.get(StackingRule, mapping.stacking_rule_id) if mapping else None

        qty_shipping_pack = _d(oi.normalized_shipping_pack_qty or oi.sap_delivery_qty or oi.qty)
        gross_weight_per_pack = _d(packaging.gross_weight_per_pack_kg if packaging else None)
        if gross_weight_per_pack == 0 and qty_shipping_pack > 0:
            gross_weight_per_pack = _d(oi.gross_weight_total_kg) / qty_shipping_pack
        if gross_weight_per_pack == 0:
            gross_weight_per_pack = _d(product.gross_weight_kg)

        total_weight = _d(oi.gross_weight_total_kg) or (qty_shipping_pack * gross_weight_per_pack)

        case_volume = _d(packaging.case_volume_m3 if packaging else None)
        if case_volume == 0 and qty_shipping_pack > 0:
            case_volume = _d(oi.volume_total_m3) / qty_shipping_pack
        if case_volume == 0:
            case_volume = _d(product.volume_m3)

        total_volume = _d(oi.volume_total_m3) or (qty_shipping_pack * case_volume)

        max_stack_layer = int(stack_rule.max_stack_layer if stack_rule and stack_rule.max_stack_layer else 1)
        stack_count = ceil(float(qty_shipping_pack) / max(max_stack_layer, 1))

        length_mm = _d(packaging.length_mm if packaging else None)
        width_mm = _d(packaging.width_mm if packaging else None)
        height_mm = _d(packaging.height_mm if packaging else None)
        required_floor_area = Decimal("0")
        required_height = Decimal("0")
        fit_notes = None
        if length_mm > 0 and width_mm > 0:
            required_floor_area = ((length_mm * width_mm) / Decimal("1000000")) * Decimal(stack_count)
            required_height = height_mm * Decimal(max_stack_layer)
        else:
            fit_notes = "missing_dimensions"

        db.add(
            CubicationRunItem(
                run_id=run.run_id,
                order_item_id=oi.order_item_id,
                product_id=oi.product_id,
                packaging_id=oi.packaging_id,
                stacking_rule_id=stack_rule.stacking_rule_id if stack_rule else None,
                qty_shipping_pack=qty_shipping_pack,
                gross_weight_per_pack_kg=gross_weight_per_pack,
                total_weight_kg=total_weight,
                length_mm=length_mm if length_mm > 0 else None,
                width_mm=width_mm if width_mm > 0 else None,
                height_mm=height_mm if height_mm > 0 else None,
                case_volume_m3=case_volume,
                total_volume_m3=total_volume,
                max_stack_layer=max_stack_layer,
                stack_layers_used=max_stack_layer,
                stack_count=stack_count,
                required_floor_area_m2=required_floor_area if required_floor_area > 0 else None,
                required_height_mm=required_height if required_height > 0 else None,
                fit_notes=fit_notes,
            )
        )
        aggregated.total_weight_kg += total_weight
        aggregated.total_volume_m3 += total_volume
        aggregated.total_required_floor_area_m2 += required_floor_area
        aggregated.required_height_mm = max(aggregated.required_height_mm, required_height)
        aggregated.total_stack_count += stack_count

    lane_rules = db.scalars(
        select(VendorLaneAllocation)
        .where(VendorLaneAllocation.customer_code == (customer.customer_code if customer else None), VendorLaneAllocation.is_active.is_(True))
    ).all()
    lane_priority = {l.truck_type_id: l.priority_no for l in lane_rules}

    trucks = db.scalars(select(TruckType).where(TruckType.is_active.is_(True))).all()
    pass_candidates: list[CubicationCandidate] = []
    partial_candidates: list[CubicationCandidate] = []

    for truck in trucks:
        eff_payload = _d(truck.max_payload_kg) * Decimal("0.95")
        pass_weight = aggregated.total_weight_kg <= eff_payload if eff_payload > 0 else False
        pass_volume = aggregated.total_volume_m3 <= _d(truck.cargo_volume_m3) if _d(truck.cargo_volume_m3) > 0 else False
        pass_floor = aggregated.total_required_floor_area_m2 <= _d(truck.deck_area_m2) if _d(truck.deck_area_m2) > 0 else None
        pass_height = aggregated.required_height_mm <= _d(truck.internal_height_mm) if _d(truck.internal_height_mm) > 0 else None

        pass_customer = True
        if customer_constraint and customer_constraint.allowed_truck_group:
            pass_customer = truck.truck_group == customer_constraint.allowed_truck_group

        weight_util = (aggregated.total_weight_kg / eff_payload * 100) if eff_payload > 0 else Decimal("0")
        volume_util = (aggregated.total_volume_m3 / _d(truck.cargo_volume_m3) * 100) if _d(truck.cargo_volume_m3) > 0 else Decimal("0")
        floor_util = (aggregated.total_required_floor_area_m2 / _d(truck.deck_area_m2) * 100) if _d(truck.deck_area_m2) > 0 else Decimal("0")
        lane_bonus = Decimal(max(0, 10 - lane_priority.get(truck.truck_type_id, 10))) / Decimal("10")

        full_pass = pass_weight and pass_volume and (pass_floor is not False) and (pass_height is not False) and pass_customer
        score = None
        rejection_reason = None
        if full_pass:
            score = (Decimal("0.35") * min(weight_util, Decimal("100"))) + (Decimal("0.35") * min(volume_util, Decimal("100"))) + (Decimal("0.2") * min(floor_util, Decimal("100"))) + (Decimal("10") * lane_bonus)
        else:
            rejection_reason = "WEIGHT" if not pass_weight else "VOLUME" if not pass_volume else "FLOOR_AREA" if pass_floor is False else "HEIGHT" if pass_height is False else "CUSTOMER_CONSTRAINT"

        candidate = CubicationCandidate(
            run_id=run.run_id,
            truck_type_id=truck.truck_type_id,
            total_weight_kg=aggregated.total_weight_kg,
            total_volume_m3=aggregated.total_volume_m3,
            total_required_floor_area_m2=aggregated.total_required_floor_area_m2,
            pass_weight=pass_weight,
            pass_volume=pass_volume,
            pass_floor_area=pass_floor,
            pass_height=pass_height,
            pass_customer_constraint=pass_customer,
            weight_utilization_pct=weight_util,
            volume_utilization_pct=volume_util,
            floor_utilization_pct=floor_util,
            score=score,
            rejection_reason=rejection_reason,
        )
        db.add(candidate)
        (pass_candidates if full_pass else partial_candidates).append(candidate)

    db.flush()
    pass_candidates.sort(key=lambda c: (c.score or Decimal("0")), reverse=True)
    for i, candidate in enumerate(pass_candidates, start=1):
        candidate.rank_no = i

    result_status = "no_fit"
    reason = "No feasible truck based on constraints"
    recommended_truck_type_id = None
    split_recommendation = None

    if pass_candidates:
        result_status = "success"
        recommended_truck_type_id = pass_candidates[0].truck_type_id
        reason = "Best-fit truck selected by composite score"
    elif partial_candidates:
        biggest_payload = max((_d(t.max_payload_kg) for t in trucks), default=Decimal("0"))
        biggest_volume = max((_d(t.cargo_volume_m3) for t in trucks), default=Decimal("0"))
        split_count = max(
            ceil(float(aggregated.total_weight_kg / biggest_payload)) if biggest_payload > 0 else 0,
            ceil(float(aggregated.total_volume_m3 / biggest_volume)) if biggest_volume > 0 else 0,
        )
        if split_count > 1:
            result_status = "split_recommendation"
            reason = f"No single truck fit. Suggest split into {split_count} groups"
            split_recommendation = [f"Group-{i}" for i in range(1, split_count + 1)]
        else:
            result_status = "manual_review"
            reason = "Partial pass candidates detected; planner validation required"

    db.add(
        CubicationResult(
            run_id=run.run_id,
            recommended_truck_type_id=recommended_truck_type_id,
            recommendation_status=result_status,
            total_weight_kg=aggregated.total_weight_kg,
            total_volume_m3=aggregated.total_volume_m3,
            total_required_floor_area_m2=aggregated.total_required_floor_area_m2,
            total_stack_count=aggregated.total_stack_count,
            recommendation_reason=reason,
            result_json={"split_recommendation": split_recommendation} if split_recommendation else {},
        )
    )

    run.status = "completed"
    run.run_finished_at = datetime.now(UTC)
    db.commit()
    db.refresh(run)
    return run
