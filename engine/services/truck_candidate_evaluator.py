from __future__ import annotations

from dataclasses import dataclass

from engine.models import CandidateEvaluation, CubicationRunItem, CustomerConstraint, LaneRule, TruckType


@dataclass
class AggregatedLoad:
    total_weight_kg: float
    total_volume_m3: float
    required_floor_area_m2: float | None
    required_height_mm: float | None


class TruckCandidateEvaluator:
    def __init__(self, odol_safety_factor: float = 1.0) -> None:
        self.odol_safety_factor = odol_safety_factor

    def aggregate(self, run_items: list[CubicationRunItem]) -> AggregatedLoad:
        return AggregatedLoad(
            total_weight_kg=sum(x.total_weight_kg for x in run_items),
            total_volume_m3=sum(x.total_volume_m3 for x in run_items),
            required_floor_area_m2=(
                sum(x.required_floor_area_m2 for x in run_items if x.required_floor_area_m2 is not None)
                if any(x.required_floor_area_m2 is not None for x in run_items)
                else None
            ),
            required_height_mm=max(
                [x.required_height_mm for x in run_items if x.required_height_mm is not None], default=None
            ),
        )

    def evaluate(
        self,
        run_id: int,
        aggregated_load: AggregatedLoad,
        trucks: list[TruckType],
        customer_constraint: CustomerConstraint | None,
        lane_rules: list[LaneRule],
    ) -> list[CandidateEvaluation]:
        lane_priority = {x.truck_type_id: x.priority_no for x in lane_rules}
        candidates: list[CandidateEvaluation] = []

        for i, truck in enumerate([t for t in trucks if t.active], start=1):
            legal = truck.legal_payload_kg if truck.legal_payload_kg is not None else truck.max_payload_kg
            effective_payload_kg = min(truck.max_payload_kg, legal) * self.odol_safety_factor

            pass_weight = aggregated_load.total_weight_kg <= effective_payload_kg
            pass_volume = aggregated_load.total_volume_m3 <= truck.cargo_volume_m3

            pass_floor_area = None
            if aggregated_load.required_floor_area_m2 is not None and truck.deck_area_m2 is not None:
                pass_floor_area = aggregated_load.required_floor_area_m2 <= truck.deck_area_m2

            pass_height = None
            if aggregated_load.required_height_mm is not None and truck.internal_height_mm is not None:
                pass_height = aggregated_load.required_height_mm <= truck.internal_height_mm

            pass_customer_constraint = True
            pass_transport_mode = True
            match_source = "default"
            if customer_constraint:
                match_source = "customer_delivery_constraint"
                if customer_constraint.allowed_truck_type_ids is not None:
                    pass_customer_constraint = truck.truck_type_id in customer_constraint.allowed_truck_type_ids
                if customer_constraint.required_transport_mode is not None:
                    pass_transport_mode = truck.transport_mode == customer_constraint.required_transport_mode

            pass_lane_rule = truck.truck_type_id in lane_priority if lane_priority else True
            lane_priority_bonus = 0.0
            if pass_lane_rule and lane_priority:
                lane_priority_bonus = max(0.0, (10 - lane_priority[truck.truck_type_id]) / 10)

            weight_util = min(aggregated_load.total_weight_kg / effective_payload_kg, 1.0) if effective_payload_kg else 0.0
            volume_util = min(aggregated_load.total_volume_m3 / truck.cargo_volume_m3, 1.0) if truck.cargo_volume_m3 else 0.0
            if aggregated_load.required_floor_area_m2 is not None and truck.deck_area_m2:
                floor_util = min(aggregated_load.required_floor_area_m2 / truck.deck_area_m2, 1.0)
            else:
                floor_util = 0.0

            full_pass = all(
                x is True or x is None
                for x in [pass_weight, pass_volume, pass_floor_area, pass_height, pass_customer_constraint, pass_lane_rule, pass_transport_mode]
            )
            score = None
            if full_pass:
                score = (weight_util * 0.35) + (volume_util * 0.25) + (floor_util * 0.30) + (lane_priority_bonus * 0.10)

            rejection_reason = None
            if not full_pass:
                if not pass_weight:
                    rejection_reason = "WEIGHT"
                elif not pass_volume:
                    rejection_reason = "VOLUME"
                elif pass_floor_area is False:
                    rejection_reason = "FLOOR_AREA"
                elif pass_height is False:
                    rejection_reason = "HEIGHT"
                elif not pass_customer_constraint:
                    rejection_reason = "CUSTOMER_CONSTRAINT"
                elif not pass_transport_mode:
                    rejection_reason = "TRANSPORT_MODE"
                elif not pass_lane_rule:
                    rejection_reason = "LANE_RULE"

            candidates.append(
                CandidateEvaluation(
                    candidate_id=i,
                    run_id=run_id,
                    truck_type_id=truck.truck_type_id,
                    pass_weight=pass_weight,
                    pass_volume=pass_volume,
                    pass_floor_area=pass_floor_area,
                    pass_height=pass_height,
                    pass_customer_constraint=pass_customer_constraint,
                    pass_lane_rule=pass_lane_rule,
                    pass_transport_mode=pass_transport_mode,
                    match_source=match_source,
                    rejection_reason_code=rejection_reason,
                    score=score,
                    rank_no=None,
                    weight_utilization_pct=weight_util * 100,
                    volume_utilization_pct=volume_util * 100,
                    floor_utilization_pct=floor_util * 100,
                    lane_priority_bonus=lane_priority_bonus,
                )
            )

        passers = sorted(
            [x for x in candidates if x.score is not None],
            key=lambda c: (c.score, c.lane_priority_bonus),
            reverse=True,
        )
        for rank, c in enumerate(passers, start=1):
            c.rank_no = rank
        return candidates
