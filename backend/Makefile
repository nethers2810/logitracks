.PHONY: install run lint migrate seed

install:
	pip install -r requirements.txt

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

migrate:
	alembic upgrade head

seed:
	python -m seeders.seed_stacking_rules

check:
	python -m compileall app
