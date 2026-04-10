from __future__ import annotations

from math import ceil

from engine.models import CubicationRunItem, OrderItem
from engine.services.stack_rule_resolver import StackRuleResolver


class CubicationCalculator:
    def __init__(self, stack_rule_resolver: StackRuleResolver | None = None) -> None:
        self.stack_rule_resolver = stack_rule_resolver or StackRuleResolver()

    def build_run_item(self, run_id: int, run_item_id: int, item: OrderItem) -> tuple[CubicationRunItem, bool]:
        qty_shipping_pack = item.normalized_shipping_pack_qty or item.sap_delivery_qty

        gross_weight_per_pack_kg = item.packaging_gross_weight_per_pack_kg
        if gross_weight_per_pack_kg is None:
            gross_weight_per_pack_kg = (item.sap_total_weight_kg or 0.0) / max(qty_shipping_pack, 1)

        total_weight_kg = item.sap_total_weight_kg
        if total_weight_kg is None:
            total_weight_kg = qty_shipping_pack * gross_weight_per_pack_kg

        case_volume_m3 = item.packaging_case_volume_m3
        if case_volume_m3 is None:
            case_volume_m3 = (item.sap_total_volume_m3 or 0.0) / max(qty_shipping_pack, 1)

        total_volume_m3 = item.sap_total_volume_m3
        if total_volume_m3 is None:
            total_volume_m3 = qty_shipping_pack * case_volume_m3

        max_stack_layer, stack_assumption = self.stack_rule_resolver.resolve_max_stack_layer(item.max_stack_layer)
        stack_layers_used = max_stack_layer
        stack_count = ceil(qty_shipping_pack / max_stack_layer)

        has_dims = all(v is not None for v in (item.length_mm, item.width_mm, item.height_mm))
        if has_dims:
            area_per_pack_m2 = (item.length_mm * item.width_mm) / 1_000_000
            required_floor_area_m2 = stack_count * area_per_pack_m2
            required_height_mm = item.height_mm * stack_layers_used
        else:
            area_per_pack_m2 = None
            required_floor_area_m2 = None
            required_height_mm = None
            stack_assumption = True

        run_item = CubicationRunItem(
            run_item_id=run_item_id,
            run_id=run_id,
            order_item_id=item.order_item_id,
            qty_shipping_pack=qty_shipping_pack,
            gross_weight_per_pack_kg=gross_weight_per_pack_kg,
            total_weight_kg=total_weight_kg,
            case_volume_m3=case_volume_m3,
            total_volume_m3=total_volume_m3,
            max_stack_layer=max_stack_layer,
            stack_layers_used=stack_layers_used,
            stack_count=stack_count,
            stack_count_est=stack_count,
            area_per_pack_m2=area_per_pack_m2,
            required_floor_area_m2=required_floor_area_m2,
            required_height_mm=required_height_mm,
            is_stacking_assumption=stack_assumption,
        )
        return run_item, stack_assumption
