.PHONY: install run migrate seed seed-demo import-demo engine-demo test check

install:
	pip install -r requirements.txt

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

migrate:
	alembic upgrade head

seed:
	python -m seeders.seed_demo_data

seed-demo:
	python -m seeders.seed_demo_data

import-demo:
	python -m seeders.import_demo_sap

engine-demo:
	python -m seeders.engine_demo

test:
	pytest backend/tests frontend/tests -q

check:
	python -m compileall app
