from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Optional


@dataclass
class OrderItem:
    order_item_id: int
    sap_delivery_qty: float
    normalized_shipping_pack_qty: Optional[float] = None
    sap_total_weight_kg: Optional[float] = None
    sap_total_volume_m3: Optional[float] = None
    packaging_gross_weight_per_pack_kg: Optional[float] = None
    packaging_case_volume_m3: Optional[float] = None
    length_mm: Optional[float] = None
    width_mm: Optional[float] = None
    height_mm: Optional[float] = None
    max_stack_layer: Optional[int] = None


@dataclass
class CubicationRun:
    run_id: int
    order_id: int
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class CubicationRunItem:
    run_item_id: int
    run_id: int
    order_item_id: int
    qty_shipping_pack: float
    gross_weight_per_pack_kg: float
    total_weight_kg: float
    case_volume_m3: float
    total_volume_m3: float
    max_stack_layer: int
    stack_layers_used: int
    stack_count: int
    stack_count_est: int
    area_per_pack_m2: Optional[float]
    required_floor_area_m2: Optional[float]
    required_height_mm: Optional[float]
    is_stacking_assumption: bool = False


@dataclass
class TruckType:
    truck_type_id: int
    name: str
    max_payload_kg: float
    cargo_volume_m3: float
    deck_area_m2: Optional[float] = None
    internal_height_mm: Optional[float] = None
    legal_payload_kg: Optional[float] = None
    active: bool = True
    transport_mode: Optional[str] = None


@dataclass
class CustomerConstraint:
    allowed_truck_type_ids: Optional[set[int]] = None
    required_transport_mode: Optional[str] = None


@dataclass
class LaneRule:
    truck_type_id: int
    priority_no: int


@dataclass
class CandidateEvaluation:
    candidate_id: int
    run_id: int
    truck_type_id: int
    pass_weight: bool
    pass_volume: bool
    pass_floor_area: Optional[bool]
    pass_height: Optional[bool]
    pass_customer_constraint: bool
    pass_lane_rule: bool
    pass_transport_mode: bool
    match_source: str
    rejection_reason_code: Optional[str]
    score: Optional[float]
    rank_no: Optional[int]
    weight_utilization_pct: float
    volume_utilization_pct: float
    floor_utilization_pct: float
    lane_priority_bonus: float


@dataclass
class CubicationResult:
    result_id: int
    run_id: int
    status: str
    recommended_truck_type_id: Optional[int]
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class CubicationSplitPlan:
    split_plan_id: int
    run_id: int
    split_group_no: int
    truck_type_id: Optional[int]
    estimated_weight_kg: float
    estimated_volume_m3: float
    estimated_stack_count: int
    status: str
    notes: Optional[str]
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class CubicationSplitPlanItem:
    split_plan_item_id: int
    split_plan_id: int
    order_item_id: int
    allocated_qty_shipping_pack: float
    allocated_weight_kg: float
    allocated_volume_m3: float
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
