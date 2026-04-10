from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class OrderBase(BaseModel):
    order_no: str | None = None
    customer_id: int
    requested_delivery_date: date | None = None
    planned_delivery_date: date | None = None
    status: str | None = None


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    order_no: str | None = None
    customer_id: int | None = None
    requested_delivery_date: date | None = None
    planned_delivery_date: date | None = None
    status: str | None = None


class OrderRead(OrderBase, ORMModel):
    order_id: int
    created_at: datetime
    updated_at: datetime


class OrderItemBase(BaseModel):
    order_id: int
    product_id: int
    packaging_id: int | None = None
    line_no: int
    qty: Decimal | None = None
    qty_uom: str | None = None
    sap_delivery_qty: Decimal | None = None
    sap_delivery_uom: str | None = None
    sap_actual_qty: Decimal | None = None
    sap_base_uom: str | None = None
    conversion_factor: Decimal | None = None


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemUpdate(BaseModel):
    packaging_id: int | None = None
    line_no: int | None = None
    qty: Decimal | None = None
    qty_uom: str | None = None
    sap_delivery_qty: Decimal | None = None
    sap_delivery_uom: str | None = None
    sap_actual_qty: Decimal | None = None
    sap_base_uom: str | None = None
    conversion_factor: Decimal | None = None


class OrderItemRead(OrderItemBase, ORMModel):
    order_item_id: int
    created_at: datetime
    updated_at: datetime


class OrderItemEnriched(BaseModel):
    order_item_id: int
    line_no: int
    product_id: int
    product_name: str | None = None
    packaging_id: int | None = None
    packaging_code: str | None = None
    stacking_rule_id: int | None = None
    stacking_rule_code: str | None = None
    qty: Decimal | None = None
    sap_delivery_qty: Decimal | None = None
    sap_actual_qty: Decimal | None = None
    estimated_stack_count: int | None = None


class CandidateTruckOverview(BaseModel):
    truck_type_id: int
    truck_name: str | None = None
    score: Decimal | None = None
    rank_no: int | None = None
    pass_weight: bool | None = None
    pass_volume: bool | None = None


class OrderSimulationPreview(BaseModel):
    order_id: int
    order_no: str | None = None
    total_weight_kg: Decimal
    total_volume_m3: Decimal
    estimated_stack_count: int
    item_count: int
    items: list[OrderItemEnriched]
    candidates: list[CandidateTruckOverview]
