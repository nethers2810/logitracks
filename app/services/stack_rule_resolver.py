from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session


class StackRuleResolver:
    def __init__(self, session: Session) -> None:
        self.session = session

    def resolve(
        self,
        category: str | None,
        subcategory: str | None,
        pack_size_label: str | None,
        sap_product_type: str | None,
    ) -> tuple[int | None, str, bool]:
        direct = self.session.execute(
            text(
                """
                SELECT max_layers
                FROM master.stacking_rule
                WHERE is_active = true
                  AND (:category IS NULL OR category = :category)
                  AND (:subcategory IS NULL OR subcategory = :subcategory)
                  AND (:pack_size_label IS NULL OR pack_size_label = :pack_size_label)
                ORDER BY
                    (category = :category)::int DESC,
                    (subcategory = :subcategory)::int DESC,
                    (pack_size_label = :pack_size_label)::int DESC
                LIMIT 1
                """
            ),
            {
                "category": category,
                "subcategory": subcategory,
                "pack_size_label": pack_size_label,
            },
        ).first()
        if direct:
            return int(direct[0]), "exact", False

        if sap_product_type:
            fuzzy = self.session.execute(
                text(
                    """
                    SELECT max_layers
                    FROM master.stacking_rule
                    WHERE is_active = true
                      AND upper(:sap_product_type) LIKE '%' || upper(rule_code) || '%'
                    ORDER BY length(rule_code) DESC
                    LIMIT 1
                    """
                ),
                {"sap_product_type": sap_product_type},
            ).first()
            if fuzzy:
                return int(fuzzy[0]), "product_type_pattern", False

        return None, "manual_review", True
