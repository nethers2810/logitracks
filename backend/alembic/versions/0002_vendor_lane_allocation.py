"""legacy vendor lane allocation branch placeholder

Revision ID: 0002_vendor_lane_allocation
Revises: 0001_initial_foundation
Create Date: 2026-04-10 00:00:01.000000
"""

revision = "0002_vendor_lane_allocation"
down_revision = "0001_initial_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # No-op on purpose: table creation lives in 0002_stage4_api_extensions.
    # Keep this revision for compatibility with existing revision history.
    pass


def downgrade() -> None:
    pass
