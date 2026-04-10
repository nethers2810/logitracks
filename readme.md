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
python seeders/seed_sample_orders.py
python -m src.main
```
