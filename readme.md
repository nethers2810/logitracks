# LogiTracks Monorepo

This repository contains the LogiTracks backend API, frontend UI, and supporting data/engine modules.

---

## 1) Prerequisites

Install these before starting:

- Docker + Docker Compose v2 (`docker compose version`)
- (Optional for local non-Docker backend) Python 3.12+
- (Optional) `make`

Verify Docker is running:

```bash
docker version
docker compose version
```

---

## 2) Quick start (recommended: full Docker)

From repository root (`/workspace/logitracks`):

### Which `.env` file is used?

- **Docker Compose workflow (commands run from repo root):** uses **root `.env`** (`/workspace/logitracks/.env`).
- **Local backend workflow (`cd backend` + `make run`):** uses **`backend/.env`**.
- For `docker compose run --rm backend ...`, only root `.env` / shell env are used by Compose for service env injection.

### Step A — Prepare environment file

```bash
cp .env.example .env
```

### Step B — Build and start services

```bash
docker compose up -d --build
```

This starts:

- `postgres` on `localhost:5432`
- `backend` on `http://localhost:8000`
- `frontend` on `http://localhost:3000`

### Step C — Confirm services are healthy

```bash
docker compose ps
docker compose logs postgres --tail=50
docker compose logs backend --tail=100
```

### Step D — Open the app

- Backend API docs: `http://localhost:8000/docs`
- Backend health: `http://localhost:8000/api/health`
- Frontend UI: `http://localhost:3000`

---

## 3) Database migrations and seeds (Docker workflow)

Run all commands from repository root.

### Run latest migrations

```bash
docker compose run --rm backend alembic upgrade head
```

### Seed demo users and demo data

```bash
docker compose run --rm backend python -m seeders.seed_demo_data
```

Demo users:

- `admin@logitracks.local` / `admin123`
- `planner@logitracks.local` / `planner123`
- `analyst@logitracks.local` / `analyst123`

> Change demo credentials before any real deployment.

---

## 4) Most common issue: `Temporary failure in name resolution`

If you get this error while running:

```bash
docker compose run --rm backend alembic upgrade head
```

and see:

- `psycopg.OperationalError: [Errno -3] Temporary failure in name resolution`

it usually means the DB host in `DATABASE_URL` is not resolvable **inside** Docker.

### Why this happens

Inside Compose, backend should connect to PostgreSQL using hostname:

- `postgres` (the Compose service name)

If `BACKEND_DATABASE_URL` is set in your shell/CI to another host (for example `db`, `localhost`, or a stale value), it overrides the Compose default and breaks name resolution.
Also, changing only `backend/.env` will not fix Docker Compose runs; for Docker, update root `.env` (or unset conflicting shell vars).

### Fix checklist

1. Inspect effective backend DB URL:

```bash
docker compose config | sed -n '/backend:/,/^[^ ]/p'
```

2. Ensure URL host is `postgres`:

```text
postgresql+psycopg://logitracks:logitracks@postgres:5432/logitracks
```

3. If your shell has an override, clear it and retry:

```bash
unset BACKEND_DATABASE_URL
docker compose run --rm backend alembic upgrade head
```

4. If needed, recreate containers/networks:

```bash
docker compose down --remove-orphans
docker compose up -d postgres
docker compose run --rm backend alembic upgrade head
```

5. Validate DNS from backend container:

```bash
docker compose run --rm backend getent hosts postgres
```

If this command returns an IP, Docker DNS is working.

---

## 5) Alternative: run backend locally (without Docker backend)

You can run only PostgreSQL in Docker and execute backend in local Python.

### Step A — Start DB only

```bash
docker compose up -d postgres
```

### Step B — Setup backend

```bash
cd backend
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
make install
```

### Step C — Configure DB URL in `backend/.env`

For local backend process, use localhost:

```env
DATABASE_URL=postgresql+psycopg://logitracks:logitracks@localhost:5432/logitracks
```

### Step D — Migrate, seed, run

```bash
make migrate
make seed-demo
make run
```

Backend docs: `http://localhost:8000/docs`

---

## 6) Frontend local serving (optional)

If you want static local serving from source:

```bash
cd frontend
python -m http.server 8080
```

Open: `http://localhost:8080`

---

## 7) Handy operations

From repository root:

```bash
# Start everything
docker compose up -d --build

# Stop everything
docker compose down

# Follow backend logs
docker compose logs -f backend

# Run backend tests in container
docker compose run --rm backend pytest
```

From `backend/` (local Python workflow):

```bash
make migrate
make seed-demo
make import-demo
make engine-demo
make test
```

---

## 8) Production notes

- Inject secrets (`JWT_SECRET_KEY`, DB creds) from a secure secret manager.
- Keep `alembic upgrade head` in startup/CI before app boot.
- Run behind reverse proxy + TLS.
- Remove demo users and bootstrap real users from internal IAM.
- Configure backups + retention before handling real traffic.
