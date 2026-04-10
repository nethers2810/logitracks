# LogiTracks Backend (Stage 1)

FastAPI backend skeleton with PostgreSQL and Alembic foundation.

## Prerequisites

- Docker + Docker Compose

## Run with Docker Compose

From repo root:

```bash
docker compose up --build
```

Services:

- Backend API: `http://localhost:8000`
- OpenAPI docs: `http://localhost:8000/docs`
- Health endpoint: `http://localhost:8000/api/health`
- Frontend placeholder: `http://localhost:3000`
- PostgreSQL: `localhost:5432`

On startup, backend runs `alembic upgrade head` before launching Uvicorn.

## Local backend-only run (without Docker)

From `backend/`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL='postgresql+psycopg://logitracks:logitracks@localhost:5432/logitracks'
alembic upgrade head
uvicorn app.main:app --reload
```

## Project skeleton

- `app/main.py`: FastAPI bootstrap and router registration
- `app/core/config.py`: settings/configuration
- `app/core/exceptions.py`: base error model and handlers
- `app/db/session.py`: SQLAlchemy engine and session factory
- `app/db/models/`: SQLAlchemy models grouped by schema
- `alembic/`: migration config and first migration
