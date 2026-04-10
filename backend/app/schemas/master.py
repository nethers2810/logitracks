from datetime import date, datetime, time
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ProductBase(BaseModel):
    sku_code: str
    sap_material_code: str | None = None
    product_name: str | None = None
    category_name: str | None = None
    subcategory_name: str | None = None
    gross_weight_kg: Decimal | None = None
    volume_m3: Decimal | None = None
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    sku_code: str | None = None
    product_name: str | None = None
    category_name: str | None = None
    subcategory_name: str | None = None
    gross_weight_kg: Decimal | None = None
    volume_m3: Decimal | None = None
    is_active: bool | None = None


class ProductRead(ProductBase, ORMModel):
    product_id: int
    created_at: datetime
    updated_at: datetime


class ProductPackagingBase(BaseModel):
    product_id: int
    packaging_code: str | None = None
    packaging_level: str | None = None
    qty_per_pack: Decimal | None = None
    case_volume_m3: Decimal | None = None
    gross_weight_per_pack_kg: Decimal | None = None
    is_default_shipping_pack: bool = False


class ProductPackagingCreate(ProductPackagingBase):
    pass


class ProductPackagingUpdate(BaseModel):
    packaging_code: str | None = None
    packaging_level: str | None = None
    qty_per_pack: Decimal | None = None
    case_volume_m3: Decimal | None = None
    gross_weight_per_pack_kg: Decimal | None = None
    is_default_shipping_pack: bool | None = None


class ProductPackagingRead(ProductPackagingBase, ORMModel):
    packaging_id: int
    created_at: datetime
    updated_at: datetime


class StackingRuleBase(BaseModel):
    rule_code: str | None = None
    category_name: str | None = None
    subcategory_name: str | None = None
    pack_size_label: str | None = None
    max_stack_layer: int | None = None
    max_stack_height_mm: Decimal | None = None
    is_active: bool = True


class StackingRuleCreate(StackingRuleBase):
    pass


class StackingRuleUpdate(BaseModel):
    rule_code: str | None = None
    category_name: str | None = None
    subcategory_name: str | None = None
    pack_size_label: str | None = None
    max_stack_layer: int | None = None
    max_stack_height_mm: Decimal | None = None
    is_active: bool | None = None


class StackingRuleRead(StackingRuleBase, ORMModel):
    stacking_rule_id: int
    created_at: datetime
    updated_at: datetime


class ProductStackingMapBase(BaseModel):
    product_id: int
    packaging_id: int | None = None
    stacking_rule_id: int
    mapping_basis: str | None = None
    mapping_confidence: Decimal | None = None
    is_manual_override: bool = False


class ProductStackingMapCreate(ProductStackingMapBase):
    pass


class ProductStackingMapUpdate(BaseModel):
    packaging_id: int | None = None
    stacking_rule_id: int | None = None
    mapping_basis: str | None = None
    mapping_confidence: Decimal | None = None
    is_manual_override: bool | None = None


class ProductStackingMapRead(ProductStackingMapBase, ORMModel):
    product_stacking_map_id: int
    created_at: datetime
    updated_at: datetime


class TruckTypeBase(BaseModel):
    truck_code: str | None = None
    truck_name: str | None = None
    truck_group: str | None = None
    cargo_volume_m3: Decimal | None = None
    max_payload_kg: Decimal | None = None
    is_active: bool = True


class TruckTypeCreate(TruckTypeBase):
    pass


class TruckTypeUpdate(BaseModel):
    truck_code: str | None = None
    truck_name: str | None = None
    truck_group: str | None = None
    cargo_volume_m3: Decimal | None = None
    max_payload_kg: Decimal | None = None
    is_active: bool | None = None


class TruckTypeRead(TruckTypeBase, ORMModel):
    truck_type_id: int
    created_at: datetime
    updated_at: datetime


class TruckAxlePolicyBase(BaseModel):
    truck_type_id: int
    axle_config: str | None = None
    legal_payload_kg: Decimal | None = None


class TruckAxlePolicyCreate(TruckAxlePolicyBase):
    pass


class TruckAxlePolicyUpdate(BaseModel):
    axle_config: str | None = None
    legal_payload_kg: Decimal | None = None


class TruckAxlePolicyRead(TruckAxlePolicyBase, ORMModel):
    truck_axle_policy_id: int
    created_at: datetime
    updated_at: datetime


class CustomerBase(BaseModel):
    customer_code: str | None = None
    customer_name: str | None = None
    city: str | None = None
    zone: str | None = None
    region: str | None = None
    tat_days: int | None = None
    is_active: bool = True


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    customer_code: str | None = None
    customer_name: str | None = None
    city: str | None = None
    zone: str | None = None
    region: str | None = None
    tat_days: int | None = None
    is_active: bool | None = None


class CustomerRead(CustomerBase, ORMModel):
    customer_id: int
    created_at: datetime
    updated_at: datetime


class CustomerDeliveryConstraintBase(BaseModel):
    customer_id: int
    max_truck_height_mm: Decimal | None = None
    max_truck_payload_kg: Decimal | None = None
    allowed_truck_group: str | None = None
    time_window_start: time | None = None
    time_window_end: time | None = None


class CustomerDeliveryConstraintCreate(CustomerDeliveryConstraintBase):
    pass


class CustomerDeliveryConstraintUpdate(BaseModel):
    max_truck_height_mm: Decimal | None = None
    max_truck_payload_kg: Decimal | None = None
    allowed_truck_group: str | None = None
    time_window_start: time | None = None
    time_window_end: time | None = None


class CustomerDeliveryConstraintRead(CustomerDeliveryConstraintBase, ORMModel):
    customer_delivery_constraint_id: int
    created_at: datetime
    updated_at: datetime


class VendorLaneAllocationBase(BaseModel):
    ship_to_code: str | None = None
    customer_code: str | None = None
    city: str | None = None
    zone: str | None = None
    region: str | None = None
    route_code: str | None = None
    truck_type_id: int
    priority_no: int
    is_active: bool = True
    notes: str | None = None


class VendorLaneAllocationCreate(VendorLaneAllocationBase):
    pass


class VendorLaneAllocationUpdate(BaseModel):
    ship_to_code: str | None = None
    customer_code: str | None = None
    city: str | None = None
    zone: str | None = None
    region: str | None = None
    route_code: str | None = None
    truck_type_id: int | None = None
    priority_no: int | None = None
    is_active: bool | None = None
    notes: str | None = None


class VendorLaneAllocationRead(VendorLaneAllocationBase, ORMModel):
    vendor_lane_allocation_id: int
    created_at: datetime
    updated_at: datetime
