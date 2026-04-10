from datetime import date, datetime, time
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, Time, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Product(Base):
    __tablename__ = "product"
    __table_args__ = (
        Index("ix_master_product_sku_code", "sku_code"),
        Index("ix_master_product_category_name", "category_name"),
        {"schema": "master"},
    )

    product_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sku_code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    sap_material_code: Mapped[str | None] = mapped_column(String(100))
    product_name: Mapped[str | None] = mapped_column(String(255))
    material_description: Mapped[str | None] = mapped_column(Text)
    product_group_raw: Mapped[str | None] = mapped_column(String(255))
    brand_name: Mapped[str | None] = mapped_column(String(255))
    category_name: Mapped[str | None] = mapped_column(String(255))
    subcategory_name: Mapped[str | None] = mapped_column(String(255))
    base_uom: Mapped[str | None] = mapped_column(String(32))
    order_uom: Mapped[str | None] = mapped_column(String(32))
    gross_weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(14, 4))
    net_weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(14, 4))
    volume_m3: Mapped[Decimal | None] = mapped_column(Numeric(14, 6))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    source_system: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class ProductPackaging(Base):
    __tablename__ = "product_packaging"
    __table_args__ = (
        Index("ix_master_product_packaging_product_id", "product_id"),
        Index("ix_master_product_packaging_packaging_code", "packaging_code"),
        {"schema": "master"},
    )

    packaging_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("master.product.product_id"), nullable=False)
    packaging_level: Mapped[str | None] = mapped_column(String(64))
    packaging_code: Mapped[str | None] = mapped_column(String(128))
    qty_per_pack: Mapped[Decimal | None] = mapped_column(Numeric(14, 4))
    length_mm: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    width_mm: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    height_mm: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    dimension_uom: Mapped[str | None] = mapped_column(String(16))
    case_volume_m3: Mapped[Decimal | None] = mapped_column(Numeric(14, 6))
    gross_weight_per_pack_kg: Mapped[Decimal | None] = mapped_column(Numeric(14, 4))
    net_weight_per_pack_kg: Mapped[Decimal | None] = mapped_column(Numeric(14, 4))
    allow_rotation: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    default_orientation: Mapped[str | None] = mapped_column(String(64))
    is_default_shipping_pack: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    is_stackable: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class StackingRule(Base):
    __tablename__ = "stacking_rule"
    __table_args__ = ({"schema": "master"},)

    stacking_rule_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rule_code: Mapped[str | None] = mapped_column(String(100), unique=True)
    category_name: Mapped[str | None] = mapped_column(String(255))
    subcategory_name: Mapped[str | None] = mapped_column(String(255))
    pack_size_label: Mapped[str | None] = mapped_column(String(100))
    max_stack_layer: Mapped[int | None] = mapped_column(Integer)
    max_stack_height_mm: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    notes: Mapped[str | None] = mapped_column(Text)
    source_document: Mapped[str | None] = mapped_column(String(255))
    effective_date: Mapped[date | None] = mapped_column(Date)
    expiry_date: Mapped[date | None] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class ProductStackingMap(Base):
    __tablename__ = "product_stacking_map"
    __table_args__ = (
        UniqueConstraint("product_id", "packaging_id", "stacking_rule_id", name="uq_master_product_stacking_map_keys"),
        Index("ix_master_product_stacking_map_product_id", "product_id"),
        Index("ix_master_product_stacking_map_packaging_id", "packaging_id"),
        Index("ix_master_product_stacking_map_stacking_rule_id", "stacking_rule_id"),
        {"schema": "master"},
    )

    product_stacking_map_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("master.product.product_id"), nullable=False)
    packaging_id: Mapped[int | None] = mapped_column(ForeignKey("master.product_packaging.packaging_id"))
    stacking_rule_id: Mapped[int] = mapped_column(ForeignKey("master.stacking_rule.stacking_rule_id"), nullable=False)
    mapping_basis: Mapped[str | None] = mapped_column(String(100))
    mapping_confidence: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    is_manual_override: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class TruckType(Base):
    __tablename__ = "truck_type"
    __table_args__ = ({"schema": "master"},)

    truck_type_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    truck_code: Mapped[str | None] = mapped_column(String(64), unique=True)
    truck_name: Mapped[str | None] = mapped_column(String(255))
    truck_group: Mapped[str | None] = mapped_column(String(100))
    internal_length_mm: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    internal_width_mm: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    internal_height_mm: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    cargo_volume_m3: Mapped[Decimal | None] = mapped_column(Numeric(14, 6))
    deck_area_m2: Mapped[Decimal | None] = mapped_column(Numeric(14, 6))
    max_payload_kg: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    tare_weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    max_gvw_kg: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    max_stack_height_allowed_mm: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    odol_safety_factor_default: Mapped[Decimal | None] = mapped_column(Numeric(6, 3))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class TruckAxlePolicy(Base):
    __tablename__ = "truck_axle_policy"
    __table_args__ = (
        Index("ix_master_truck_axle_policy_truck_type_id", "truck_type_id"),
        {"schema": "master"},
    )

    truck_axle_policy_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    truck_type_id: Mapped[int] = mapped_column(ForeignKey("master.truck_type.truck_type_id"), nullable=False)
    axle_config: Mapped[str | None] = mapped_column(String(100))
    legal_payload_kg: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    odol_warning_threshold_pct: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    odol_block_threshold_pct: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    road_restriction_notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class Customer(Base):
    __tablename__ = "customer"
    __table_args__ = ({"schema": "master"},)

    customer_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_code: Mapped[str | None] = mapped_column(String(100), unique=True)
    customer_name: Mapped[str | None] = mapped_column(String(255))
    city: Mapped[str | None] = mapped_column(String(100))
    zone: Mapped[str | None] = mapped_column(String(100))
    region: Mapped[str | None] = mapped_column(String(100))
    tat_days: Mapped[int | None] = mapped_column(Integer)
    address_line: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class CustomerDeliveryConstraint(Base):
    __tablename__ = "customer_delivery_constraint"
    __table_args__ = (
        Index("ix_master_customer_delivery_constraint_customer_id", "customer_id"),
        {"schema": "master"},
    )

    customer_delivery_constraint_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("master.customer.customer_id"), nullable=False)
    max_truck_length_mm: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    max_truck_width_mm: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    max_truck_height_mm: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    max_truck_payload_kg: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    allowed_truck_group: Mapped[str | None] = mapped_column(String(100))
    time_window_start: Mapped[time | None] = mapped_column(Time)
    time_window_end: Mapped[time | None] = mapped_column(Time)
    road_access_notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
