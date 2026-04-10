from __future__ import annotations

import csv
import json
from pathlib import Path

from .models import CargoItem

REQUIRED_FIELDS = {
    "sku",
    "cargo_type",
    "length_cm",
    "width_cm",
    "height_cm",
    "quantity",
    "weight_kg",
}


def _parse_row(row: dict[str, str]) -> CargoItem:
    missing = REQUIRED_FIELDS - set(row)
    if missing:
        raise ValueError(f"missing required fields: {sorted(missing)}")

    return CargoItem(
        sku=row["sku"],
        cargo_type=row["cargo_type"],
        length_cm=float(row["length_cm"]),
        width_cm=float(row["width_cm"]),
        height_cm=float(row["height_cm"]),
        quantity=int(row["quantity"]),
        weight_kg=float(row["weight_kg"]),
    )


def import_csv(path: str | Path) -> list[CargoItem]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [_parse_row(row) for row in reader]


def import_json(path: str | Path) -> list[CargoItem]:
    with open(path, encoding="utf-8") as f:
        payload = json.load(f)

    if not isinstance(payload, list):
        raise ValueError("JSON payload must be a list of items")

    return [_parse_row(item) for item in payload]
