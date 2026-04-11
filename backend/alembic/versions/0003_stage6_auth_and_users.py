"""stage6 auth and users

Revision ID: 0003_stage6_auth_and_users
Revises: 0002_stage4_api_extensions
Create Date: 2026-04-10 00:00:02.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "0003_stage6_auth_and_users"
down_revision = ("0002_stage4_api_extensions", "0002_vendor_lane_allocation")
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "app_user",
        sa.Column("user_id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="public",
    )


def downgrade() -> None:
    op.drop_table("app_user", schema="public")
