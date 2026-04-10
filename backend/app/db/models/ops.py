from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class OrderHeader(Base):
    __tablename__ = "order_header"
    __table_args__ = (
        Index("ix_ops_order_header_customer_id", "customer_id"),
        {"schema": "ops"},
    )

    order_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_no: Mapped[str | None] = mapped_column(String(100), unique=True)
    source_order_type: Mapped[str | None] = mapped_column(String(100))
    source_reference_no: Mapped[str | None] = mapped_column(String(100))
    customer_id: Mapped[int] = mapped_column(ForeignKey("master.customer.customer_id"), nullable=False)
    requested_delivery_date: Mapped[date | None] = mapped_column(Date)
    planned_delivery_date: Mapped[date | None] = mapped_column(Date)
    origin_location_code: Mapped[str | None] = mapped_column(String(100))
    destination_location_code: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class OrderItem(Base):
    __tablename__ = "order_item"
    __table_args__ = (
        UniqueConstraint("order_id", "line_no", name="uq_ops_order_item_order_line"),
        Index("ix_ops_order_item_order_id", "order_id"),
        Index("ix_ops_order_item_product_id", "product_id"),
        Index("ix_ops_order_item_packaging_id", "packaging_id"),
        {"schema": "ops"},
    )

    order_item_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("ops.order_header.order_id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("master.product.product_id"), nullable=False)
    packaging_id: Mapped[int | None] = mapped_column(ForeignKey("master.product_packaging.packaging_id"))
    line_no: Mapped[int] = mapped_column(Integer, nullable=False)
    qty: Mapped[Decimal | None] = mapped_column(Numeric(14, 4))
    qty_uom: Mapped[str | None] = mapped_column(String(32))
    sap_delivery_qty: Mapped[Decimal | None] = mapped_column(Numeric(14, 4))
    sap_delivery_uom: Mapped[str | None] = mapped_column(String(30))
    sap_actual_qty: Mapped[Decimal | None] = mapped_column(Numeric(14, 4))
    sap_base_uom: Mapped[str | None] = mapped_column(String(30))
    conversion_factor: Mapped[Decimal | None] = mapped_column(Numeric(14, 6))
    normalized_shipping_pack_qty: Mapped[Decimal | None] = mapped_column(Numeric(14, 4))
    gross_weight_total_kg: Mapped[Decimal | None] = mapped_column(Numeric(14, 4))
    volume_total_m3: Mapped[Decimal | None] = mapped_column(Numeric(14, 6))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
