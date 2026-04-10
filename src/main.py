from .engine import evaluate_cubication
from .import_pipeline import import_json


if __name__ == "__main__":
    items = import_json("data/sample_orders.json")
    result = evaluate_cubication(items)
    print(result)
