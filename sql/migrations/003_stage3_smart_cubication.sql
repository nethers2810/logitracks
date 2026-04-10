-- Stage 3 Smart Cubication Engine schema updates

CREATE TABLE IF NOT EXISTS engine.cubication_split_plan (
    split_plan_id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL REFERENCES engine.cubication_run(run_id),
    split_group_no INTEGER NOT NULL,
    truck_type_id BIGINT NULL REFERENCES master.truck_type(truck_type_id),
    estimated_weight_kg NUMERIC(18,4) NOT NULL,
    estimated_volume_m3 NUMERIC(18,6) NOT NULL,
    estimated_stack_count INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL,
    notes TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS engine.cubication_split_plan_item (
    split_plan_item_id BIGSERIAL PRIMARY KEY,
    split_plan_id BIGINT NOT NULL REFERENCES engine.cubication_split_plan(split_plan_id),
    order_item_id BIGINT NOT NULL REFERENCES sales.order_item(order_item_id),
    allocated_qty_shipping_pack NUMERIC(18,4) NOT NULL,
    allocated_weight_kg NUMERIC(18,4) NOT NULL,
    allocated_volume_m3 NUMERIC(18,6) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

ALTER TABLE engine.cubication_candidate
    ADD COLUMN IF NOT EXISTS pass_lane_rule BOOLEAN,
    ADD COLUMN IF NOT EXISTS pass_transport_mode BOOLEAN,
    ADD COLUMN IF NOT EXISTS match_source VARCHAR(100),
    ADD COLUMN IF NOT EXISTS rejection_reason_code VARCHAR(50);
