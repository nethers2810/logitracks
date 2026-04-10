from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.exceptions import AppError
from app.db.models.ops import OrderHeader, OrderItem
from app.schemas.common import PaginationMeta
from app.schemas.ops import OrderCreate, OrderItemCreate, OrderItemRead, OrderItemUpdate, OrderRead, OrderSimulationPreview, OrderUpdate
from app.services.crud import CRUDService
from app.services.dashboard import get_order_simulation_preview

router = APIRouter(prefix="/orders")
order_service = CRUDService(OrderHeader, "order_id", ["order_no", "status"], ["order_no"])
order_item_service = CRUDService(OrderItem, "order_item_id", ["qty_uom", "line_no"])


@router.get("")
def list_orders(page: int = 1, page_size: int = 20, sort_by: str | None = None, sort_order: str = "desc", q: str | None = None, customer_id: int | None = None, status_filter: str | None = None, db: Session = Depends(get_db)):
    items, total = order_service.list(
        db,
        page,
        page_size,
        sort_by,
        sort_order,
        q,
        filters={"customer_id": customer_id, "status": status_filter},
    )
    return {"items": items, "meta": PaginationMeta(page=page, page_size=page_size, total=total)}


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    return order_service.create(db, payload.model_dump())


@router.get("/{order_id}", response_model=OrderRead)
def get_order(order_id: int, db: Session = Depends(get_db)):
    return order_service.get(db, order_id)


@router.put("/{order_id}", response_model=OrderRead)
def update_order(order_id: int, payload: OrderUpdate, db: Session = Depends(get_db)):
    return order_service.update(db, order_id, payload.model_dump(exclude_unset=True))


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    order_service.delete(db, order_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{order_id}/items")
def list_order_items(order_id: int, page: int = 1, page_size: int = 50, sort_by: str | None = None, sort_order: str = "asc", q: str | None = None, db: Session = Depends(get_db)):
    if not db.get(OrderHeader, order_id):
        raise AppError("Order not found", status_code=404, code="not_found")
    items, total = order_item_service.list(db, page, page_size, sort_by, sort_order, q, filters={"order_id": order_id})
    return {"items": items, "meta": PaginationMeta(page=page, page_size=page_size, total=total)}


@router.post("/{order_id}/items", response_model=OrderItemRead, status_code=status.HTTP_201_CREATED)
def create_order_item(order_id: int, payload: OrderItemCreate, db: Session = Depends(get_db)):
    if payload.order_id != order_id:
        raise AppError("order_id in payload must match path", status_code=422, code="validation_error")
    return order_item_service.create(db, payload.model_dump())


@router.get("/{order_id}/items/{order_item_id}", response_model=OrderItemRead)
def get_order_item(order_id: int, order_item_id: int, db: Session = Depends(get_db)):
    item = order_item_service.get(db, order_item_id)
    if item.order_id != order_id:
        raise AppError("Order item not found in order", status_code=404, code="not_found")
    return item


@router.put("/{order_id}/items/{order_item_id}", response_model=OrderItemRead)
def update_order_item(order_id: int, order_item_id: int, payload: OrderItemUpdate, db: Session = Depends(get_db)):
    existing = db.get(OrderItem, order_item_id)
    if not existing or existing.order_id != order_id:
        raise AppError("Order item not found in order", status_code=404, code="not_found")
    return order_item_service.update(db, order_item_id, payload.model_dump(exclude_unset=True))


@router.delete("/{order_id}/items/{order_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order_item(order_id: int, order_item_id: int, db: Session = Depends(get_db)):
    existing = db.get(OrderItem, order_item_id)
    if not existing or existing.order_id != order_id:
        raise AppError("Order item not found in order", status_code=404, code="not_found")
    order_item_service.delete(db, order_item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{order_id}/simulation-preview", response_model=OrderSimulationPreview)
def simulation_preview(order_id: int, db: Session = Depends(get_db)):
    try:
        return get_order_simulation_preview(db, order_id)
    except ValueError as exc:
        raise AppError(str(exc), status_code=404, code="not_found") from exc
