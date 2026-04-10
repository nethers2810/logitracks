-- Stage 2 imports and normalization

CREATE SCHEMA IF NOT EXISTS audit;
CREATE SCHEMA IF NOT EXISTS master;
CREATE SCHEMA IF NOT EXISTS ops;
CREATE SCHEMA IF NOT EXISTS engine;

ALTER TABLE IF EXISTS ops.order_item
    ADD COLUMN IF NOT EXISTS sap_delivery_qty numeric,
    ADD COLUMN IF NOT EXISTS sap_delivery_uom varchar(30),
    ADD COLUMN IF NOT EXISTS sap_actual_qty numeric,
    ADD COLUMN IF NOT EXISTS sap_base_uom varchar(30),
    ADD COLUMN IF NOT EXISTS conversion_factor numeric,
    ADD COLUMN IF NOT EXISTS sap_total_weight_kg numeric,
    ADD COLUMN IF NOT EXISTS sap_total_volume_m3 numeric,
    ADD COLUMN IF NOT EXISTS sap_route varchar(80),
    ADD COLUMN IF NOT EXISTS sap_product_type varchar(120),
    ADD COLUMN IF NOT EXISTS sap_br varchar(80),
    ADD COLUMN IF NOT EXISTS sap_region varchar(80),
    ADD COLUMN IF NOT EXISTS sap_channel varchar(80);

ALTER TABLE IF EXISTS engine.cubication_run_item
    ADD COLUMN IF NOT EXISTS stack_rule_source varchar(50),
    ADD COLUMN IF NOT EXISTS stack_layers_allowed integer,
    ADD COLUMN IF NOT EXISTS stack_count_est numeric,
    ADD COLUMN IF NOT EXISTS is_stacking_assumption boolean DEFAULT false,
    ADD COLUMN IF NOT EXISTS stacking_note text;

CREATE TABLE IF NOT EXISTS master.vendor_lane_allocation (
    vendor_lane_allocation_id bigserial PRIMARY KEY,
    ship_to_code varchar(40) NULL,
    customer_code varchar(40) NULL,
    city varchar(120) NULL,
    zone varchar(120) NULL,
    region varchar(120) NULL,
    route_code varchar(80) NULL,
    truck_type_id bigint NOT NULL REFERENCES master.truck_type(truck_type_id),
    priority_no integer NOT NULL,
    is_active boolean NOT NULL DEFAULT true,
    notes text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS audit.source_import_log (
    source_import_log_id bigserial PRIMARY KEY,
    source_type varchar(50) NOT NULL,
    file_name varchar(255) NOT NULL,
    status varchar(50) NOT NULL,
    row_count integer NOT NULL DEFAULT 0,
    processed_rows integer NOT NULL DEFAULT 0,
    error_rows integer NOT NULL DEFAULT 0,
    started_at timestamptz NOT NULL DEFAULT now(),
    finished_at timestamptz NULL
);

CREATE TABLE IF NOT EXISTS audit.validation_error (
    validation_error_id bigserial PRIMARY KEY,
    source_import_log_id bigint NOT NULL REFERENCES audit.source_import_log(source_import_log_id),
    row_number integer NULL,
    field_name varchar(80) NULL,
    error_code varchar(50) NOT NULL,
    error_message text NOT NULL,
    raw_payload jsonb NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_order_header_source_delivery
    ON ops.order_header(source_system, source_delivery_no);

CREATE UNIQUE INDEX IF NOT EXISTS uq_order_item_natural
    ON ops.order_item(order_header_id, line_seq, material_code);

CREATE INDEX IF NOT EXISTS idx_validation_error_import_log
    ON audit.validation_error(source_import_log_id);
