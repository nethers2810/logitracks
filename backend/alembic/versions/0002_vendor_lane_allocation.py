"""add vendor lane allocation

Revision ID: 0002_vendor_lane_allocation
Revises: 0001_initial_foundation
Create Date: 2026-04-10 00:00:01.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_vendor_lane_allocation"
down_revision = "0001_initial_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "vendor_lane_allocation",
        sa.Column("vendor_lane_allocation_id", sa.Integer(), primary_key=True),
        sa.Column("ship_to_code", sa.String(length=100), nullable=True),
        sa.Column("customer_code", sa.String(length=100), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("zone", sa.String(length=100), nullable=True),
        sa.Column("region", sa.String(length=100), nullable=True),
        sa.Column("route_code", sa.String(length=100), nullable=True),
        sa.Column("truck_type_id", sa.Integer(), sa.ForeignKey("master.truck_type.truck_type_id"), nullable=True),
        sa.Column("priority_no", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        schema="master",
    )


def downgrade() -> None:
    op.drop_table("vendor_lane_allocation", schema="master")
