"""initial foundation

Revision ID: 0001_initial_foundation
Revises:
Create Date: 2026-04-10 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0001_initial_foundation"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    for schema in ("master", "ops", "engine", "audit"):
        op.execute(sa.text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))

    op.create_table(
        "product",
        sa.Column("product_id", sa.Integer(), primary_key=True),
        sa.Column("sku_code", sa.String(length=100), nullable=False, unique=True),
        sa.Column("sap_material_code", sa.String(length=100), nullable=True),
        sa.Column("product_name", sa.String(length=255), nullable=True),
        sa.Column("material_description", sa.Text(), nullable=True),
        sa.Column("product_group_raw", sa.String(length=255), nullable=True),
        sa.Column("brand_name", sa.String(length=255), nullable=True),
        sa.Column("category_name", sa.String(length=255), nullable=True),
        sa.Column("subcategory_name", sa.String(length=255), nullable=True),
        sa.Column("base_uom", sa.String(length=32), nullable=True),
        sa.Column("order_uom", sa.String(length=32), nullable=True),
        sa.Column("gross_weight_kg", sa.Numeric(14, 4), nullable=True),
        sa.Column("net_weight_kg", sa.Numeric(14, 4), nullable=True),
        sa.Column("volume_m3", sa.Numeric(14, 6), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("source_system", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="master",
    )
    op.create_index("ix_master_product_sku_code", "product", ["sku_code"], schema="master")
    op.create_index("ix_master_product_category_name", "product", ["category_name"], schema="master")

    op.create_table(
        "product_packaging",
        sa.Column("packaging_id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("master.product.product_id"), nullable=False),
        sa.Column("packaging_level", sa.String(length=64), nullable=True),
        sa.Column("packaging_code", sa.String(length=128), nullable=True),
        sa.Column("qty_per_pack", sa.Numeric(14, 4), nullable=True),
        sa.Column("length_mm", sa.Numeric(14, 2), nullable=True),
        sa.Column("width_mm", sa.Numeric(14, 2), nullable=True),
        sa.Column("height_mm", sa.Numeric(14, 2), nullable=True),
        sa.Column("dimension_uom", sa.String(length=16), nullable=True),
        sa.Column("case_volume_m3", sa.Numeric(14, 6), nullable=True),
        sa.Column("gross_weight_per_pack_kg", sa.Numeric(14, 4), nullable=True),
        sa.Column("net_weight_per_pack_kg", sa.Numeric(14, 4), nullable=True),
        sa.Column("allow_rotation", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("default_orientation", sa.String(length=64), nullable=True),
        sa.Column("is_default_shipping_pack", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_stackable", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="master",
    )
    op.create_index("ix_master_product_packaging_product_id", "product_packaging", ["product_id"], schema="master")
    op.create_index("ix_master_product_packaging_packaging_code", "product_packaging", ["packaging_code"], schema="master")

    op.create_table(
        "stacking_rule",
        sa.Column("stacking_rule_id", sa.Integer(), primary_key=True),
        sa.Column("rule_code", sa.String(length=100), nullable=True, unique=True),
        sa.Column("category_name", sa.String(length=255), nullable=True),
        sa.Column("subcategory_name", sa.String(length=255), nullable=True),
        sa.Column("pack_size_label", sa.String(length=100), nullable=True),
        sa.Column("max_stack_layer", sa.Integer(), nullable=True),
        sa.Column("max_stack_height_mm", sa.Numeric(14, 2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("source_document", sa.String(length=255), nullable=True),
        sa.Column("effective_date", sa.Date(), nullable=True),
        sa.Column("expiry_date", sa.Date(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="master",
    )

    op.create_table(
        "truck_type",
        sa.Column("truck_type_id", sa.Integer(), primary_key=True),
        sa.Column("truck_code", sa.String(length=64), nullable=True, unique=True),
        sa.Column("truck_name", sa.String(length=255), nullable=True),
        sa.Column("truck_group", sa.String(length=100), nullable=True),
        sa.Column("internal_length_mm", sa.Numeric(14, 2), nullable=True),
        sa.Column("internal_width_mm", sa.Numeric(14, 2), nullable=True),
        sa.Column("internal_height_mm", sa.Numeric(14, 2), nullable=True),
        sa.Column("cargo_volume_m3", sa.Numeric(14, 6), nullable=True),
        sa.Column("deck_area_m2", sa.Numeric(14, 6), nullable=True),
        sa.Column("max_payload_kg", sa.Numeric(14, 2), nullable=True),
        sa.Column("tare_weight_kg", sa.Numeric(14, 2), nullable=True),
        sa.Column("max_gvw_kg", sa.Numeric(14, 2), nullable=True),
        sa.Column("max_stack_height_allowed_mm", sa.Numeric(14, 2), nullable=True),
        sa.Column("odol_safety_factor_default", sa.Numeric(6, 3), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="master",
    )

    op.create_table(
        "customer",
        sa.Column("customer_id", sa.Integer(), primary_key=True),
        sa.Column("customer_code", sa.String(length=100), nullable=True, unique=True),
        sa.Column("customer_name", sa.String(length=255), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("zone", sa.String(length=100), nullable=True),
        sa.Column("region", sa.String(length=100), nullable=True),
        sa.Column("tat_days", sa.Integer(), nullable=True),
        sa.Column("address_line", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="master",
    )

    op.create_table(
        "product_stacking_map",
        sa.Column("product_stacking_map_id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("master.product.product_id"), nullable=False),
        sa.Column("packaging_id", sa.Integer(), sa.ForeignKey("master.product_packaging.packaging_id"), nullable=True),
        sa.Column("stacking_rule_id", sa.Integer(), sa.ForeignKey("master.stacking_rule.stacking_rule_id"), nullable=False),
        sa.Column("mapping_basis", sa.String(length=100), nullable=True),
        sa.Column("mapping_confidence", sa.Numeric(5, 2), nullable=True),
        sa.Column("is_manual_override", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("product_id", "packaging_id", "stacking_rule_id", name="uq_master_product_stacking_map_keys"),
        schema="master",
    )
    op.create_index("ix_master_product_stacking_map_product_id", "product_stacking_map", ["product_id"], schema="master")
    op.create_index("ix_master_product_stacking_map_packaging_id", "product_stacking_map", ["packaging_id"], schema="master")
    op.create_index("ix_master_product_stacking_map_stacking_rule_id", "product_stacking_map", ["stacking_rule_id"], schema="master")

    op.create_table(
        "truck_axle_policy",
        sa.Column("truck_axle_policy_id", sa.Integer(), primary_key=True),
        sa.Column("truck_type_id", sa.Integer(), sa.ForeignKey("master.truck_type.truck_type_id"), nullable=False),
        sa.Column("axle_config", sa.String(length=100), nullable=True),
        sa.Column("legal_payload_kg", sa.Numeric(14, 2), nullable=True),
        sa.Column("odol_warning_threshold_pct", sa.Numeric(6, 2), nullable=True),
        sa.Column("odol_block_threshold_pct", sa.Numeric(6, 2), nullable=True),
        sa.Column("road_restriction_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="master",
    )
    op.create_index("ix_master_truck_axle_policy_truck_type_id", "truck_axle_policy", ["truck_type_id"], schema="master")

    op.create_table(
        "customer_delivery_constraint",
        sa.Column("customer_delivery_constraint_id", sa.Integer(), primary_key=True),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("master.customer.customer_id"), nullable=False),
        sa.Column("max_truck_length_mm", sa.Numeric(14, 2), nullable=True),
        sa.Column("max_truck_width_mm", sa.Numeric(14, 2), nullable=True),
        sa.Column("max_truck_height_mm", sa.Numeric(14, 2), nullable=True),
        sa.Column("max_truck_payload_kg", sa.Numeric(14, 2), nullable=True),
        sa.Column("allowed_truck_group", sa.String(length=100), nullable=True),
        sa.Column("time_window_start", sa.Time(), nullable=True),
        sa.Column("time_window_end", sa.Time(), nullable=True),
        sa.Column("road_access_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="master",
    )
    op.create_index(
        "ix_master_customer_delivery_constraint_customer_id",
        "customer_delivery_constraint",
        ["customer_id"],
        schema="master",
    )

    op.create_table(
        "order_header",
        sa.Column("order_id", sa.Integer(), primary_key=True),
        sa.Column("order_no", sa.String(length=100), nullable=True, unique=True),
        sa.Column("source_order_type", sa.String(length=100), nullable=True),
        sa.Column("source_reference_no", sa.String(length=100), nullable=True),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("master.customer.customer_id"), nullable=False),
        sa.Column("requested_delivery_date", sa.Date(), nullable=True),
        sa.Column("planned_delivery_date", sa.Date(), nullable=True),
        sa.Column("origin_location_code", sa.String(length=100), nullable=True),
        sa.Column("destination_location_code", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="ops",
    )
    op.create_index("ix_ops_order_header_customer_id", "order_header", ["customer_id"], schema="ops")

    op.create_table(
        "order_item",
        sa.Column("order_item_id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("ops.order_header.order_id"), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("master.product.product_id"), nullable=False),
        sa.Column("packaging_id", sa.Integer(), sa.ForeignKey("master.product_packaging.packaging_id"), nullable=True),
        sa.Column("line_no", sa.Integer(), nullable=False),
        sa.Column("qty", sa.Numeric(14, 4), nullable=True),
        sa.Column("qty_uom", sa.String(length=32), nullable=True),
        sa.Column("normalized_shipping_pack_qty", sa.Numeric(14, 4), nullable=True),
        sa.Column("gross_weight_total_kg", sa.Numeric(14, 4), nullable=True),
        sa.Column("volume_total_m3", sa.Numeric(14, 6), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("order_id", "line_no", name="uq_ops_order_item_order_line"),
        schema="ops",
    )
    op.create_index("ix_ops_order_item_order_id", "order_item", ["order_id"], schema="ops")
    op.create_index("ix_ops_order_item_product_id", "order_item", ["product_id"], schema="ops")
    op.create_index("ix_ops_order_item_packaging_id", "order_item", ["packaging_id"], schema="ops")

    op.create_table(
        "cubication_run",
        sa.Column("run_id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("ops.order_header.order_id"), nullable=False),
        sa.Column("algorithm_version", sa.String(length=100), nullable=True),
        sa.Column("calculation_mode", sa.String(length=100), nullable=True),
        sa.Column("odol_safety_factor", sa.Numeric(6, 3), nullable=True),
        sa.Column("floor_utilization_limit_pct", sa.Numeric(6, 2), nullable=True),
        sa.Column("volume_utilization_limit_pct", sa.Numeric(6, 2), nullable=True),
        sa.Column("weight_utilization_limit_pct", sa.Numeric(6, 2), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.Column("run_started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("run_finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="engine",
    )
    op.create_index("ix_engine_cubication_run_order_id", "cubication_run", ["order_id"], schema="engine")

    op.create_table(
        "cubication_run_item",
        sa.Column("run_item_id", sa.Integer(), primary_key=True),
        sa.Column("run_id", sa.Integer(), sa.ForeignKey("engine.cubication_run.run_id"), nullable=False),
        sa.Column("order_item_id", sa.Integer(), sa.ForeignKey("ops.order_item.order_item_id"), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("master.product.product_id"), nullable=False),
        sa.Column("packaging_id", sa.Integer(), sa.ForeignKey("master.product_packaging.packaging_id"), nullable=True),
        sa.Column("stacking_rule_id", sa.Integer(), sa.ForeignKey("master.stacking_rule.stacking_rule_id"), nullable=True),
        sa.Column("qty_shipping_pack", sa.Numeric(14, 4), nullable=True),
        sa.Column("gross_weight_per_pack_kg", sa.Numeric(14, 4), nullable=True),
        sa.Column("total_weight_kg", sa.Numeric(14, 4), nullable=True),
        sa.Column("length_mm", sa.Numeric(14, 2), nullable=True),
        sa.Column("width_mm", sa.Numeric(14, 2), nullable=True),
        sa.Column("height_mm", sa.Numeric(14, 2), nullable=True),
        sa.Column("case_volume_m3", sa.Numeric(14, 6), nullable=True),
        sa.Column("total_volume_m3", sa.Numeric(14, 6), nullable=True),
        sa.Column("max_stack_layer", sa.Integer(), nullable=True),
        sa.Column("stack_layers_used", sa.Integer(), nullable=True),
        sa.Column("stack_count", sa.Integer(), nullable=True),
        sa.Column("required_floor_area_m2", sa.Numeric(14, 6), nullable=True),
        sa.Column("required_height_mm", sa.Numeric(14, 2), nullable=True),
        sa.Column("fit_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="engine",
    )
    op.create_index("ix_engine_cubication_run_item_run_id", "cubication_run_item", ["run_id"], schema="engine")
    op.create_index("ix_engine_cubication_run_item_order_item_id", "cubication_run_item", ["order_item_id"], schema="engine")

    op.create_table(
        "cubication_candidate",
        sa.Column("candidate_id", sa.Integer(), primary_key=True),
        sa.Column("run_id", sa.Integer(), sa.ForeignKey("engine.cubication_run.run_id"), nullable=False),
        sa.Column("truck_type_id", sa.Integer(), sa.ForeignKey("master.truck_type.truck_type_id"), nullable=False),
        sa.Column("total_weight_kg", sa.Numeric(14, 4), nullable=True),
        sa.Column("total_volume_m3", sa.Numeric(14, 6), nullable=True),
        sa.Column("total_required_floor_area_m2", sa.Numeric(14, 6), nullable=True),
        sa.Column("pass_weight", sa.Boolean(), nullable=True),
        sa.Column("pass_volume", sa.Boolean(), nullable=True),
        sa.Column("pass_floor_area", sa.Boolean(), nullable=True),
        sa.Column("pass_height", sa.Boolean(), nullable=True),
        sa.Column("pass_customer_constraint", sa.Boolean(), nullable=True),
        sa.Column("weight_utilization_pct", sa.Numeric(6, 2), nullable=True),
        sa.Column("volume_utilization_pct", sa.Numeric(6, 2), nullable=True),
        sa.Column("floor_utilization_pct", sa.Numeric(6, 2), nullable=True),
        sa.Column("score", sa.Numeric(10, 4), nullable=True),
        sa.Column("rank_no", sa.Integer(), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="engine",
    )
    op.create_index("ix_engine_cubication_candidate_run_id", "cubication_candidate", ["run_id"], schema="engine")
    op.create_index(
        "ix_engine_cubication_candidate_truck_type_id",
        "cubication_candidate",
        ["truck_type_id"],
        schema="engine",
    )

    op.create_table(
        "cubication_result",
        sa.Column("result_id", sa.Integer(), primary_key=True),
        sa.Column("run_id", sa.Integer(), sa.ForeignKey("engine.cubication_run.run_id"), nullable=False),
        sa.Column("recommended_truck_type_id", sa.Integer(), sa.ForeignKey("master.truck_type.truck_type_id"), nullable=True),
        sa.Column("recommendation_status", sa.String(length=50), nullable=True),
        sa.Column("total_weight_kg", sa.Numeric(14, 4), nullable=True),
        sa.Column("total_volume_m3", sa.Numeric(14, 6), nullable=True),
        sa.Column("total_required_floor_area_m2", sa.Numeric(14, 6), nullable=True),
        sa.Column("total_stack_count", sa.Integer(), nullable=True),
        sa.Column("recommendation_reason", sa.Text(), nullable=True),
        sa.Column("result_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("run_id", name="uq_engine_cubication_result_run_id"),
        schema="engine",
    )
    op.create_index(
        "ix_engine_cubication_result_recommended_truck_type_id",
        "cubication_result",
        ["recommended_truck_type_id"],
        schema="engine",
    )

    op.create_table(
        "source_import_log",
        sa.Column("import_log_id", sa.Integer(), primary_key=True),
        sa.Column("source_name", sa.String(length=100), nullable=True),
        sa.Column("file_name", sa.String(length=255), nullable=True),
        sa.Column("import_type", sa.String(length=100), nullable=True),
        sa.Column("row_count", sa.Integer(), nullable=True),
        sa.Column("success_count", sa.Integer(), nullable=True),
        sa.Column("error_count", sa.Integer(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        schema="audit",
    )

    op.create_table(
        "validation_error",
        sa.Column("validation_error_id", sa.Integer(), primary_key=True),
        sa.Column("import_log_id", sa.Integer(), sa.ForeignKey("audit.source_import_log.import_log_id"), nullable=True),
        sa.Column("entity_name", sa.String(length=100), nullable=True),
        sa.Column("row_identifier", sa.String(length=255), nullable=True),
        sa.Column("field_name", sa.String(length=100), nullable=True),
        sa.Column("error_code", sa.String(length=100), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("severity", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="audit",
    )
    op.create_index("ix_audit_validation_error_import_log_id", "validation_error", ["import_log_id"], schema="audit")
    op.create_index("ix_audit_validation_error_entity_name", "validation_error", ["entity_name"], schema="audit")


def downgrade() -> None:
    op.drop_index("ix_audit_validation_error_entity_name", table_name="validation_error", schema="audit")
    op.drop_index("ix_audit_validation_error_import_log_id", table_name="validation_error", schema="audit")
    op.drop_table("validation_error", schema="audit")
    op.drop_table("source_import_log", schema="audit")

    op.drop_index("ix_engine_cubication_result_recommended_truck_type_id", table_name="cubication_result", schema="engine")
    op.drop_table("cubication_result", schema="engine")
    op.drop_index("ix_engine_cubication_candidate_truck_type_id", table_name="cubication_candidate", schema="engine")
    op.drop_index("ix_engine_cubication_candidate_run_id", table_name="cubication_candidate", schema="engine")
    op.drop_table("cubication_candidate", schema="engine")
    op.drop_index("ix_engine_cubication_run_item_order_item_id", table_name="cubication_run_item", schema="engine")
    op.drop_index("ix_engine_cubication_run_item_run_id", table_name="cubication_run_item", schema="engine")
    op.drop_table("cubication_run_item", schema="engine")
    op.drop_index("ix_engine_cubication_run_order_id", table_name="cubication_run", schema="engine")
    op.drop_table("cubication_run", schema="engine")

    op.drop_index("ix_ops_order_item_packaging_id", table_name="order_item", schema="ops")
    op.drop_index("ix_ops_order_item_product_id", table_name="order_item", schema="ops")
    op.drop_index("ix_ops_order_item_order_id", table_name="order_item", schema="ops")
    op.drop_table("order_item", schema="ops")
    op.drop_index("ix_ops_order_header_customer_id", table_name="order_header", schema="ops")
    op.drop_table("order_header", schema="ops")

    op.drop_index("ix_master_customer_delivery_constraint_customer_id", table_name="customer_delivery_constraint", schema="master")
    op.drop_table("customer_delivery_constraint", schema="master")
    op.drop_index("ix_master_truck_axle_policy_truck_type_id", table_name="truck_axle_policy", schema="master")
    op.drop_table("truck_axle_policy", schema="master")
    op.drop_index("ix_master_product_stacking_map_stacking_rule_id", table_name="product_stacking_map", schema="master")
    op.drop_index("ix_master_product_stacking_map_packaging_id", table_name="product_stacking_map", schema="master")
    op.drop_index("ix_master_product_stacking_map_product_id", table_name="product_stacking_map", schema="master")
    op.drop_table("product_stacking_map", schema="master")
    op.drop_table("customer", schema="master")
    op.drop_table("truck_type", schema="master")
    op.drop_table("stacking_rule", schema="master")
    op.drop_index("ix_master_product_packaging_packaging_code", table_name="product_packaging", schema="master")
    op.drop_index("ix_master_product_packaging_product_id", table_name="product_packaging", schema="master")
    op.drop_table("product_packaging", schema="master")
    op.drop_index("ix_master_product_category_name", table_name="product", schema="master")
    op.drop_index("ix_master_product_sku_code", table_name="product", schema="master")
    op.drop_table("product", schema="master")

    for schema in ("audit", "engine", "ops", "master"):
        op.execute(sa.text(f"DROP SCHEMA IF EXISTS {schema} CASCADE"))
