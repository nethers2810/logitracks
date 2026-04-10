# LogiTracks Monorepo — Stage 6 (Internal Pilot Hardening)

This repository now includes Stage 6 hardening for realistic internal use:
- JWT authentication + role-based access (`admin`, `planner`, `analyst`),
- demo seed workflow (master data → SAP order import → cubication result),
- backend and frontend smoke tests,
- deployment-oriented runbook and operational commands.

## Architecture summary

- **Backend (`backend/`)**: FastAPI, SQLAlchemy, Alembic, JWT auth, role-guarded APIs.
- **Data domains**:
  - `master.*` for products/trucks/rules/customers/lanes,
  - `ops.*` for imported orders,
  - `engine.*` for cubication runs/results,
  - `public.app_user` for internal application users.
- **Frontend (`frontend/`)**: simple internal web UI with functional login, logout, current-user header, and role-aware UI controls.

## Demo user credentials

Seeded by `python -m seeders.seed_demo_data`:

- `admin@logitracks.local` / `admin123`
- `planner@logitracks.local` / `planner123`
- `analyst@logitracks.local` / `analyst123`

> Change all demo credentials before production use.

## Local setup (sample)

### 1) Start infrastructure

```bash
docker compose up -d postgres
```

### 2) Backend setup

```bash
cd backend
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
make install
make migrate
make seed-demo
make run
```

### 3) Frontend setup (simple static serving)

```bash
cd frontend
python -m http.server 8080
```

Open:
- API docs: `http://localhost:8000/docs`
- Frontend: `http://localhost:8080`

## Stage 6 workflow commands

Run from `backend/`:

- **DB migration run command**: `make migrate`
- **Seed command**: `make seed-demo`
- **Import demo command**: `make import-demo`
- **Engine demo command**: `make engine-demo`
- **Run tests**: `make test`

## API healthchecks

- `GET /api/health`
- `GET /api/health/live`
- `GET /api/health/ready`

## Docker Compose production notes

- Use environment-specific secrets (`JWT_SECRET_KEY`, DB password) via secret manager or env-injection.
- Use a reverse proxy/TLS terminator in front of backend/frontend.
- Remove demo credentials and run user bootstrap through secure internal IAM process.
- Keep `alembic upgrade head` in startup/CI migration step before app boot.
- Configure DB backups and retention before pilot traffic.

## Future enhancements

- Dimensional cubication,
- Route optimization,
- Mixed-load rules,
- Truck availability calendar,
- 3D load planning.
