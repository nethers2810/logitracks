"""stage4 api extensions

Revision ID: 0002_stage4_api_extensions
Revises: 0001_initial_foundation
Create Date: 2026-04-10 00:00:01.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_stage4_api_extensions"
down_revision = "0001_initial_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "vendor_lane_allocation",
        sa.Column("vendor_lane_allocation_id", sa.Integer(), primary_key=True),
        sa.Column("ship_to_code", sa.String(length=40), nullable=True),
        sa.Column("customer_code", sa.String(length=40), nullable=True),
        sa.Column("city", sa.String(length=120), nullable=True),
        sa.Column("zone", sa.String(length=120), nullable=True),
        sa.Column("region", sa.String(length=120), nullable=True),
        sa.Column("route_code", sa.String(length=80), nullable=True),
        sa.Column("truck_type_id", sa.Integer(), sa.ForeignKey("master.truck_type.truck_type_id"), nullable=False),
        sa.Column("priority_no", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="master",
    )
    op.create_index(
        "ix_master_vendor_lane_allocation_customer_code",
        "vendor_lane_allocation",
        ["customer_code"],
        schema="master",
    )
    op.create_index(
        "ix_master_vendor_lane_allocation_truck_type_id",
        "vendor_lane_allocation",
        ["truck_type_id"],
        schema="master",
    )

    op.add_column("order_item", sa.Column("sap_delivery_qty", sa.Numeric(14, 4), nullable=True), schema="ops")
    op.add_column("order_item", sa.Column("sap_delivery_uom", sa.String(length=30), nullable=True), schema="ops")
    op.add_column("order_item", sa.Column("sap_actual_qty", sa.Numeric(14, 4), nullable=True), schema="ops")
    op.add_column("order_item", sa.Column("sap_base_uom", sa.String(length=30), nullable=True), schema="ops")
    op.add_column("order_item", sa.Column("conversion_factor", sa.Numeric(14, 6), nullable=True), schema="ops")


def downgrade() -> None:
    op.drop_column("order_item", "conversion_factor", schema="ops")
    op.drop_column("order_item", "sap_base_uom", schema="ops")
    op.drop_column("order_item", "sap_actual_qty", schema="ops")
    op.drop_column("order_item", "sap_delivery_uom", schema="ops")
    op.drop_column("order_item", "sap_delivery_qty", schema="ops")

    op.drop_index("ix_master_vendor_lane_allocation_truck_type_id", table_name="vendor_lane_allocation", schema="master")
    op.drop_index("ix_master_vendor_lane_allocation_customer_code", table_name="vendor_lane_allocation", schema="master")
    op.drop_table("vendor_lane_allocation", schema="master")
