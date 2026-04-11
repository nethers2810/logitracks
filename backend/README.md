# LogiTracks Backend (Internal Pilot / No-Auth Mode)

FastAPI + SQLAlchemy backend for master data, operations, import workflow, and Smart Cubication simulation.

## Pilot mode behavior

- Authentication enforcement is disabled for internal pilot routes.
- Core business endpoints are available directly without bearer tokens.
- `/api/auth/*` routes may remain available, but are not required for normal pilot flow.

## Core APIs used by pilot UI

- Dashboard: `/api/dashboard/*`
- Master data: `/api/master/*`
- Orders + detail: `/api/orders/*`
- Simulation flow: `/api/data/orders/{order_id}/simulate`, `/api/data/simulation-runs/{run_id}`
- Imports: `/api/data/imports/*`

## Setup

```bash
cd backend
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
make install
```

## Migration + seed + demo workflow

```bash
cd backend
make migrate
make seed-demo
make import-demo
make engine-demo
```

## Run

```bash
make run
```

## Testing

```bash
make test
```
