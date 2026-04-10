# LogiTracks Backend (Stage 4)

FastAPI + SQLAlchemy backend for master data CRUD, orders, import audit, cubication summaries, and dashboard APIs.

## Architecture overview

- **API Layer** (`app/api/routers/*`): thin routers for endpoint wiring and HTTP concerns.
- **Service Layer** (`app/services/*`): reusable business logic for CRUD/query operations and dashboard/simulation enrichment.
- **Schema Layer** (`app/schemas/*`): typed Pydantic request/response models.
- **Persistence Layer** (`app/db/models/*`, `app/db/session.py`): SQLAlchemy models and session management.
- **Core Infrastructure** (`app/core/*`): central config, structured logging, exception handling.

## API module map

- `GET /api/health`
- Master CRUD:
  - `/api/master/products`
  - `/api/master/product-packaging`
  - `/api/master/stacking-rules`
  - `/api/master/product-stacking-maps`
  - `/api/master/truck-types`
  - `/api/master/truck-axle-policies`
  - `/api/master/customers`
  - `/api/master/customer-delivery-constraints`
  - `/api/master/vendor-lane-allocations`
- Orders CRUD:
  - `/api/orders`
  - `/api/orders/{id}`
  - `/api/orders/{id}/items`
  - `/api/orders/{id}/simulation-preview`
- Dashboard summary:
  - `/api/dashboard/summary`
  - `/api/dashboard/recent-imports`
  - `/api/dashboard/recent-runs`
  - `/api/dashboard/recommendation-status-breakdown`

## Setup

```bash
cd backend
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
make install
```

## Migration steps

```bash
cd backend
alembic upgrade head
```

Includes:
- `0001_initial_foundation`
- `0002_stage4_api_extensions` (vendor lane allocations + SAP order item quantity fields)

## Seeding steps

```bash
cd backend
python -m seeders.seed_stacking_rules
python -m seeders.seed_sample_orders
```

## Import steps

Use the Stage-2 import endpoints (`/api/imports/*`) if your environment includes those modules, then review:

- `GET /api/dashboard/recent-imports`
- `GET /api/dashboard/summary`

## Engine run steps

1. Ensure orders and master data are loaded.
2. Execute cubication engine flows (existing engine job/runner).
3. Validate outcomes via:
   - `GET /api/dashboard/recent-runs`
   - `GET /api/dashboard/recommendation-status-breakdown`
   - `GET /api/orders/{id}/simulation-preview`

## Run API

```bash
cd backend
make run
```

Docs:
- OpenAPI: `http://localhost:8000/openapi.json`
- Swagger: `http://localhost:8000/docs`
