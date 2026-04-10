# LogiTracks Backend (Stage 6)

FastAPI + SQLAlchemy backend with authentication, role-based access, master/ops/engine APIs, and demo seeding for internal pilot use.

## Roles

- `admin`: full master data management + operational actions.
- `planner`: import SAP data, run/review engine outputs.
- `analyst`: dashboard and result visibility.

## New Stage 6 API additions

- `POST /api/auth/login`
- `GET /api/auth/me`
- `GET /api/health/live`
- `GET /api/health/ready`

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
