from __future__ import annotations

from engine.models import CustomerConstraint, LaneRule, OrderItem, TruckType
from engine.repository import InMemoryRepository
from engine.services.cubication_calculator import CubicationCalculator
from engine.services.split_planner import SplitPlanner
from engine.services.truck_candidate_evaluator import TruckCandidateEvaluator


class RecommendationService:
    def __init__(
        self,
        repository: InMemoryRepository,
        cubication_calculator: CubicationCalculator | None = None,
        truck_candidate_evaluator: TruckCandidateEvaluator | None = None,
        split_planner: SplitPlanner | None = None,
    ) -> None:
        self.repository = repository
        self.cubication_calculator = cubication_calculator or CubicationCalculator()
        self.truck_candidate_evaluator = truck_candidate_evaluator or TruckCandidateEvaluator(odol_safety_factor=0.95)
        self.split_planner = split_planner or SplitPlanner()

    def run(
        self,
        order_id: int,
        order_items: list[OrderItem],
        trucks: list[TruckType],
        customer_constraint: CustomerConstraint | None = None,
        lane_rules: list[LaneRule] | None = None,
    ) -> int:
        lane_rules = lane_rules or []
        run = self.repository.create_run(order_id)

        run_items = []
        unresolved_stack_rule = False
        for idx, item in enumerate(order_items, start=1):
            run_item, stack_assumption = self.cubication_calculator.build_run_item(run.run_id, idx, item)
            unresolved_stack_rule = unresolved_stack_rule or stack_assumption
            run_items.append(run_item)
        self.repository.save_run_items(run.run_id, run_items)

        aggregated = self.truck_candidate_evaluator.aggregate(run_items)
        candidates = self.truck_candidate_evaluator.evaluate(run.run_id, aggregated, trucks, customer_constraint, lane_rules)
        self.repository.save_candidates(run.run_id, candidates)

        full_passers = sorted([c for c in candidates if c.score is not None], key=lambda x: x.rank_no or 999)
        partial_candidates = [c for c in candidates if c.score is None and (c.pass_weight or c.pass_volume)]

        split_plans, split_plan_items = self.split_planner.create_split_plan(run.run_id, run_items, aggregated, trucks, candidates)

        if full_passers:
            self.repository.save_result(run.run_id, "success", full_passers[0].truck_type_id)
        elif split_plans:
            self.repository.save_result(run.run_id, "split_recommendation", None, notes="Split shipment suggested")
            self.repository.save_split_plan(run.run_id, split_plans, split_plan_items)
        elif partial_candidates or unresolved_stack_rule:
            self.repository.save_result(run.run_id, "manual_review", None, notes="Manual review required")
        else:
            self.repository.save_result(run.run_id, "no_fit", None, notes="No feasible truck")

        return run.run_id
