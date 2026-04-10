from __future__ import annotations

from sqlalchemy import text

from app.db import get_session

SEED_RULES = [
    ("UHT_115", 32),
    ("UHT_180", 16),
    ("UHT_225", 16),
    ("UHT_946_1000", 5),
    ("SCM_CAN_370", 28),
    ("SCM_CAN_490", 20),
    ("POUCH_280", 7),
    ("POUCH_545", 4),
    ("CHEESE_150", 8),
    ("SCM_BULK_5000", 5),
]


def main() -> None:
    with get_session() as session:
        for code, layers in SEED_RULES:
            session.execute(
                text(
                    """
                    INSERT INTO master.stacking_rule
                        (rule_code, category, subcategory, pack_size_label, max_layers, is_active, created_at, updated_at)
                    VALUES
                        (:rule_code, NULL, NULL, NULL, :max_layers, true, now(), now())
                    ON CONFLICT (rule_code)
                    DO UPDATE SET
                        max_layers = EXCLUDED.max_layers,
                        is_active = true,
                        updated_at = now()
                    """
                ),
                {"rule_code": code, "max_layers": layers},
            )
    print("Stacking rules seeded.")


if __name__ == "__main__":
    main()
