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

### Step D — Open the app (internal pilot / no-auth mode)

- Backend API docs: `http://localhost:8000/docs`
- Backend health: `http://localhost:8000/api/health`
- Frontend UI: `http://localhost:3000` (opens directly to dashboard; no login required)

### Step E — Verify core pilot workflow

1. Open `http://localhost:3000/dashboard` and confirm dashboard cards/charts render.
2. Open `http://localhost:3000/orders` and confirm order list loads.
3. Open any order detail (`http://localhost:3000/orders/<order_id>`).
4. Click **Run Smart Cubication** on order detail.
5. Open resulting simulation page (`http://localhost:3000/simulation/<run_id>`) and verify candidate trucks and recommendation result are shown.

This repository is currently configured for **internal pilot no-auth mode** so business workflow validation is not blocked by login/session failures.

---

## 3) Database migrations and seeds (Docker workflow)

Run all commands from repository root.

### Run latest migrations

```bash
docker compose run --rm backend alembic upgrade head
```

### Seed demo data

```bash
docker compose run --rm backend python -m seeders.seed_demo_data
```

---


## 4) Final troubleshooting: dashboard blank (`/dashboard`)

Jika halaman `http://localhost:3000/dashboard` kosong/blank, lakukan langkah final berikut secara berurutan dari root repo.

### Step 1 — Pastikan pakai kode terbaru (fix router legacy)

```bash
git pull
```

Fix terbaru memastikan `backend/app/api/routers/data.py` memiliki `router = APIRouter()` sehingga endpoint legacy `/api/dashboard` terdaftar dengan benar.

### Step 2 — Rebuild service backend & frontend

```bash
docker compose build backend frontend
```

### Step 3 — Restart stack

```bash
docker compose down --remove-orphans
docker compose up -d
```

### Step 4 — Verifikasi endpoint dashboard dari backend

```bash
curl -sS http://localhost:8000/api/dashboard | head
```

Expected: JSON berisi `summary`, `recentImports`, `recentRuns`, dan `recommendationBreakdown`.

### Step 5 — Cek log jika masih blank

```bash
docker compose logs backend --tail=200
docker compose logs frontend --tail=200
```

Jika masih bermasalah, kirimkan output 2 command log di atas untuk analisa lanjutan.

---

## 5) Most common issue: `Temporary failure in name resolution`

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

1. Rebuild backend image after pulling migration changes:

```bash
docker compose build backend
```

`docker compose run --rm backend ...` uses code baked into the backend image. A stale image can still have old Alembic revisions.

Quick verification (should print a line containing `extra="ignore"`):

```bash
docker compose run --rm backend sh -lc "grep -n 'extra=\"ignore\"' app/core/config.py"
```

2. Inspect effective backend DB URL:

```bash
docker compose config | sed -n '/backend:/,/^[^ ]/p'
```

3. Ensure URL host is `postgres`:

```text
postgresql+psycopg://logitracks:logitracks@postgres:5432/logitracks
```

4. If your shell has an override, clear it and retry:

```bash
unset BACKEND_DATABASE_URL
docker compose run --rm backend alembic upgrade head
```

5. If needed, recreate containers/networks:

```bash
docker compose down --remove-orphans
docker compose up -d postgres
docker compose run --rm backend alembic upgrade head
```

6. Validate DNS from backend container:

```bash
docker compose run --rm backend getent hosts postgres
```

If this command returns an IP, Docker DNS is working.

---

## 6) Alternative: run backend locally (without Docker backend)

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

## 7) Frontend local serving (optional)

If you want static local serving from source:

```bash
cd frontend
python -m http.server 8080
```

Open: `http://localhost:8080`

---

## 8) Handy operations

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

## 9) Production notes

- Inject secrets (`JWT_SECRET_KEY`, DB creds) from a secure secret manager.
- Keep `alembic upgrade head` in startup/CI before app boot.
- Run behind reverse proxy + TLS.
- Remove demo users and bootstrap real users from internal IAM.
- Configure backups + retention before handling real traffic.
