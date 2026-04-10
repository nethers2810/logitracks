from decimal import Decimal

from sqlalchemy import case, desc, func, select
from sqlalchemy.orm import Session

from app.db.models.audit import SourceImportLog
from app.db.models.engine import CubicationCandidate, CubicationResult, CubicationRun
from app.db.models.master import Customer, Product, ProductPackaging, ProductStackingMap, StackingRule, TruckType
from app.db.models.ops import OrderHeader, OrderItem


def get_dashboard_summary(db: Session) -> dict:
    total_products = db.scalar(select(func.count()).select_from(Product)) or 0
    total_customers = db.scalar(select(func.count()).select_from(Customer)) or 0
    total_trucks = db.scalar(select(func.count()).select_from(TruckType)) or 0
    total_orders = db.scalar(select(func.count()).select_from(OrderHeader)) or 0
    total_runs = db.scalar(select(func.count()).select_from(CubicationRun)) or 0

    status_counts = db.execute(
        select(
            func.sum(case((CubicationResult.recommendation_status == "manual_review", 1), else_=0)),
            func.sum(case((CubicationResult.recommendation_status == "no_fit", 1), else_=0)),
        )
    ).one()

    return {
        "total_products": total_products,
        "total_customers": total_customers,
        "total_trucks": total_trucks,
        "total_orders": total_orders,
        "total_runs": total_runs,
        "manual_review_count": status_counts[0] or 0,
        "no_fit_count": status_counts[1] or 0,
    }


def recent_imports(db: Session, limit: int = 20):
    return db.scalars(select(SourceImportLog).order_by(desc(SourceImportLog.started_at)).limit(limit)).all()


def recent_runs(db: Session, limit: int = 20):
    return db.scalars(select(CubicationRun).order_by(desc(CubicationRun.created_at)).limit(limit)).all()


def recommendation_status_breakdown(db: Session):
    rows = db.execute(
        select(CubicationResult.recommendation_status, func.count())
        .group_by(CubicationResult.recommendation_status)
        .order_by(desc(func.count()))
    ).all()
    return [{"recommendation_status": r[0] or "unknown", "count": r[1]} for r in rows]


def get_order_simulation_preview(db: Session, order_id: int) -> dict:
    order = db.get(OrderHeader, order_id)
    if not order:
        raise ValueError("Order not found")

    rows = db.execute(
        select(
            OrderItem,
            Product.product_name,
            ProductPackaging.packaging_code,
            ProductStackingMap.stacking_rule_id,
            StackingRule.rule_code,
            StackingRule.max_stack_layer,
        )
        .join(Product, Product.product_id == OrderItem.product_id)
        .outerjoin(ProductPackaging, ProductPackaging.packaging_id == OrderItem.packaging_id)
        .outerjoin(
            ProductStackingMap,
            (ProductStackingMap.product_id == OrderItem.product_id)
            & (
                (ProductStackingMap.packaging_id == OrderItem.packaging_id)
                | (ProductStackingMap.packaging_id.is_(None))
            ),
        )
        .outerjoin(StackingRule, StackingRule.stacking_rule_id == ProductStackingMap.stacking_rule_id)
        .where(OrderItem.order_id == order_id)
        .order_by(OrderItem.line_no)
    ).all()

    items = []
    total_weight = Decimal("0")
    total_volume = Decimal("0")
    total_stack = 0
    for row in rows:
        item = row[0]
        est_stack = int((item.qty or 0) / max(row[5] or 1, 1)) if item.qty else 0
        total_stack += est_stack
        total_weight += Decimal(str(item.gross_weight_total_kg or 0))
        total_volume += Decimal(str(item.volume_total_m3 or 0))
        items.append(
            {
                "order_item_id": item.order_item_id,
                "line_no": item.line_no,
                "product_id": item.product_id,
                "product_name": row[1],
                "packaging_id": item.packaging_id,
                "packaging_code": row[2],
                "stacking_rule_id": row[3],
                "stacking_rule_code": row[4],
                "qty": item.qty,
                "sap_delivery_qty": item.sap_delivery_qty,
                "sap_actual_qty": item.sap_actual_qty,
                "estimated_stack_count": est_stack,
            }
        )

    candidate_rows = db.execute(
        select(CubicationCandidate, TruckType.truck_name)
        .join(CubicationRun, CubicationRun.run_id == CubicationCandidate.run_id)
        .join(TruckType, TruckType.truck_type_id == CubicationCandidate.truck_type_id)
        .where(CubicationRun.order_id == order_id)
        .order_by(CubicationCandidate.rank_no.asc().nulls_last())
        .limit(5)
    ).all()

    candidates = [
        {
            "truck_type_id": c[0].truck_type_id,
            "truck_name": c[1],
            "score": c[0].score,
            "rank_no": c[0].rank_no,
            "pass_weight": c[0].pass_weight,
            "pass_volume": c[0].pass_volume,
        }
        for c in candidate_rows
    ]

    return {
        "order_id": order.order_id,
        "order_no": order.order_no,
        "total_weight_kg": total_weight,
        "total_volume_m3": total_volume,
        "estimated_stack_count": total_stack,
        "item_count": len(items),
        "items": items,
        "candidates": candidates,
    }
