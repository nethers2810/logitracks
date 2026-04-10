from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, JSON, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CubicationRun(Base):
    __tablename__ = "cubication_run"
    __table_args__ = (
        Index("ix_engine_cubication_run_order_id", "order_id"),
        {"schema": "engine"},
    )

    run_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("ops.order_header.order_id"), nullable=False)
    algorithm_version: Mapped[str | None] = mapped_column(String(100))
    calculation_mode: Mapped[str | None] = mapped_column(String(100))
    odol_safety_factor: Mapped[Decimal | None] = mapped_column(Numeric(6, 3))
    floor_utilization_limit_pct: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    volume_utilization_limit_pct: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    weight_utilization_limit_pct: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    status: Mapped[str | None] = mapped_column(String(50))
    run_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    run_finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class CubicationRunItem(Base):
    __tablename__ = "cubication_run_item"
    __table_args__ = (
        Index("ix_engine_cubication_run_item_run_id", "run_id"),
        Index("ix_engine_cubication_run_item_order_item_id", "order_item_id"),
        {"schema": "engine"},
    )

    run_item_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("engine.cubication_run.run_id"), nullable=False)
    order_item_id: Mapped[int] = mapped_column(ForeignKey("ops.order_item.order_item_id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("master.product.product_id"), nullable=False)
    packaging_id: Mapped[int | None] = mapped_column(ForeignKey("master.product_packaging.packaging_id"))
    stacking_rule_id: Mapped[int | None] = mapped_column(ForeignKey("master.stacking_rule.stacking_rule_id"))
    qty_shipping_pack: Mapped[Decimal | None] = mapped_column(Numeric(14, 4))
    gross_weight_per_pack_kg: Mapped[Decimal | None] = mapped_column(Numeric(14, 4))
    total_weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(14, 4))
    length_mm: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    width_mm: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    height_mm: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    case_volume_m3: Mapped[Decimal | None] = mapped_column(Numeric(14, 6))
    total_volume_m3: Mapped[Decimal | None] = mapped_column(Numeric(14, 6))
    max_stack_layer: Mapped[int | None] = mapped_column(Integer)
    stack_layers_used: Mapped[int | None] = mapped_column(Integer)
    stack_count: Mapped[int | None] = mapped_column(Integer)
    required_floor_area_m2: Mapped[Decimal | None] = mapped_column(Numeric(14, 6))
    required_height_mm: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    fit_notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class CubicationCandidate(Base):
    __tablename__ = "cubication_candidate"
    __table_args__ = (
        Index("ix_engine_cubication_candidate_run_id", "run_id"),
        Index("ix_engine_cubication_candidate_truck_type_id", "truck_type_id"),
        {"schema": "engine"},
    )

    candidate_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("engine.cubication_run.run_id"), nullable=False)
    truck_type_id: Mapped[int] = mapped_column(ForeignKey("master.truck_type.truck_type_id"), nullable=False)
    total_weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(14, 4))
    total_volume_m3: Mapped[Decimal | None] = mapped_column(Numeric(14, 6))
    total_required_floor_area_m2: Mapped[Decimal | None] = mapped_column(Numeric(14, 6))
    pass_weight: Mapped[bool | None] = mapped_column(Boolean)
    pass_volume: Mapped[bool | None] = mapped_column(Boolean)
    pass_floor_area: Mapped[bool | None] = mapped_column(Boolean)
    pass_height: Mapped[bool | None] = mapped_column(Boolean)
    pass_customer_constraint: Mapped[bool | None] = mapped_column(Boolean)
    weight_utilization_pct: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    volume_utilization_pct: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    floor_utilization_pct: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    score: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    rank_no: Mapped[int | None] = mapped_column(Integer)
    rejection_reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class CubicationResult(Base):
    __tablename__ = "cubication_result"
    __table_args__ = (
        UniqueConstraint("run_id", name="uq_engine_cubication_result_run_id"),
        Index("ix_engine_cubication_result_recommended_truck_type_id", "recommended_truck_type_id"),
        {"schema": "engine"},
    )

    result_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("engine.cubication_run.run_id"), nullable=False)
    recommended_truck_type_id: Mapped[int | None] = mapped_column(ForeignKey("master.truck_type.truck_type_id"))
    recommendation_status: Mapped[str | None] = mapped_column(String(50))
    total_weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(14, 4))
    total_volume_m3: Mapped[Decimal | None] = mapped_column(Numeric(14, 6))
    total_required_floor_area_m2: Mapped[Decimal | None] = mapped_column(Numeric(14, 6))
    total_stack_count: Mapped[int | None] = mapped_column(Integer)
    recommendation_reason: Mapped[str | None] = mapped_column(Text)
    result_json: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
