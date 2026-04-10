# Logitracks

## Stage 2 Import Pipeline

This stage adds ingestion endpoints and services for:

- SAP deliveries/orders
- Product master
- Customer master
- Truck type master
- Vendor lane allocation
- Stacking rules seed data

### Database updates

Run migration:

```bash
psql "$DATABASE_URL" -f migrations/002_stage2_imports.sql
```

The migration adds:

- SAP raw quantity/metadata fields on `ops.order_item`
- Stacking assumption/result fields on `engine.cubication_run_item`
- New `master.vendor_lane_allocation`
- Audit tables for import runs and row validation errors

### Import API

Endpoints:

- `POST /api/imports/products`
- `POST /api/imports/customers`
- `POST /api/imports/trucks`
- `POST /api/imports/vendor-allocation`
- `POST /api/imports/sap-deliveries`
- `GET /api/imports/logs`
- `GET /api/imports/logs/{id}/errors`

All upload endpoints accept `.xlsx` files parsed with `pandas` + `openpyxl`.

### Validation and audit flow

1. File upload creates a `audit.source_import_log` record with status `processing`.
2. Required columns are validated before row processing.
3. Row-level issues are persisted to `audit.validation_error`.
4. Master data imports upsert records safely using natural keys.
5. SAP normalization:
   - groups by `delivery_no` to upsert `ops.order_header`
   - upserts `ops.order_item` by `(order_header_id, line_seq, material_code)`
   - stores both SAP delivery and base quantities
   - computes `conversion_factor = sap_actual_qty / sap_delivery_qty` when valid

### Stacking rules seeding

Seed default stack limits:

```bash
python -m seeders.seed_stacking_rules
```

Initial rules:

- UHT_115 -> 32
- UHT_180 -> 16
- UHT_225 -> 16
- UHT_946_1000 -> 5
- SCM_CAN_370 -> 28
- SCM_CAN_490 -> 20
- POUCH_280 -> 7
- POUCH_545 -> 4
- CHEESE_150 -> 8
- SCM_BULK_5000 -> 5

### Stack rule resolver service

`app/services/stack_rule_resolver.py` resolves with fallback logic:

1. Exact category/subcategory/pack_size_label match.
2. `sap_product_type` pattern match against rule code.
3. Manual review flag when unresolved.

### Run API locally

```bash
uvicorn app.main:app --reload
```

Sample CSV files for initial data references are under `sample_seed_data/`.
# LogiTracks Monorepo

Stage 1 scaffold includes:

- `backend/`: FastAPI + SQLAlchemy + Alembic
- `frontend/`: placeholder static container
- `infra/`: infrastructure folder placeholder
- `docs/`: documentation folder placeholder
# Smart Cubication Engine (MVP)

This repository now contains the first cut for:

0. Build MVP for Smart Cubication Engine.
1. Implement seeders and import pipeline.
2. Implement Smart Cubication Engine backend logic.

## Structure

- `src/models.py`: domain objects (`CargoItem`, `ContainerSpec`, `CubicationResult`).
- `src/import_pipeline.py`: CSV/JSON import and validation helpers.
- `src/engine.py`: cubication calculation and container recommendation logic.
- `seeders/seed_sample_orders.py`: generates seeded sample orders.
- `src/main.py`: basic runnable example.

## Quick start

```bash
docker compose up --build
python seeders/seed_sample_orders.py
python -m src.main
```
