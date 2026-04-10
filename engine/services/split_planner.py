from __future__ import annotations

from math import ceil

from engine.models import CandidateEvaluation, CubicationRunItem, CubicationSplitPlan, CubicationSplitPlanItem, TruckType
from engine.services.truck_candidate_evaluator import AggregatedLoad


class SplitPlanner:
    def create_split_plan(
        self,
        run_id: int,
        run_items: list[CubicationRunItem],
        aggregated_load: AggregatedLoad,
        trucks: list[TruckType],
        candidates: list[CandidateEvaluation],
    ) -> tuple[list[CubicationSplitPlan], list[CubicationSplitPlanItem]]:
        if any(c.score is not None for c in candidates):
            return [], []

        max_payload = max((min(t.max_payload_kg, t.legal_payload_kg or t.max_payload_kg) for t in trucks if t.active), default=0)
        max_volume = max((t.cargo_volume_m3 for t in trucks if t.active), default=0)
        if max_payload <= 0 or max_volume <= 0:
            return [], []

        split_count = max(ceil(aggregated_load.total_weight_kg / max_payload), ceil(aggregated_load.total_volume_m3 / max_volume))
        if split_count <= 1:
            return [], []

        plans: list[CubicationSplitPlan] = []
        items: list[CubicationSplitPlanItem] = []
        for group_no in range(1, split_count + 1):
            plans.append(
                CubicationSplitPlan(
                    split_plan_id=group_no,
                    run_id=run_id,
                    split_group_no=group_no,
                    truck_type_id=None,
                    estimated_weight_kg=aggregated_load.total_weight_kg / split_count,
                    estimated_volume_m3=aggregated_load.total_volume_m3 / split_count,
                    estimated_stack_count=ceil(sum(r.stack_count for r in run_items) / split_count),
                    status="draft",
                    notes="Auto-generated split",
                )
            )

        item_counter = 1
        for group_no in range(1, split_count + 1):
            for run_item in run_items:
                allocated_qty = run_item.qty_shipping_pack / split_count
                items.append(
                    CubicationSplitPlanItem(
                        split_plan_item_id=item_counter,
                        split_plan_id=group_no,
                        order_item_id=run_item.order_item_id,
                        allocated_qty_shipping_pack=allocated_qty,
                        allocated_weight_kg=run_item.total_weight_kg / split_count,
                        allocated_volume_m3=run_item.total_volume_m3 / split_count,
                    )
                )
                item_counter += 1
        return plans, items
