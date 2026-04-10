from pathlib import Path
import json

sample_orders = [
    {
        "sku": "SKU-BOX-001",
        "cargo_type": "box",
        "length_cm": 40,
        "width_cm": 30,
        "height_cm": 20,
        "quantity": 30,
        "weight_kg": 5.5,
    },
    {
        "sku": "SKU-BOX-002",
        "cargo_type": "box",
        "length_cm": 60,
        "width_cm": 50,
        "height_cm": 45,
        "quantity": 10,
        "weight_kg": 12,
    },
]

output_path = Path("data/sample_orders.json")
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(json.dumps(sample_orders, indent=2), encoding="utf-8")
print(f"Seeded sample order data to {output_path}")
