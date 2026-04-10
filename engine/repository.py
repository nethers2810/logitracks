from __future__ import annotations

from dataclasses import dataclass, field

from engine.models import (
    CandidateEvaluation,
    CubicationResult,
    CubicationRun,
    CubicationRunItem,
    CubicationSplitPlan,
    CubicationSplitPlanItem,
)


@dataclass
class InMemoryRepository:
    runs: dict[int, CubicationRun] = field(default_factory=dict)
    run_items: dict[int, list[CubicationRunItem]] = field(default_factory=dict)
    candidates: dict[int, list[CandidateEvaluation]] = field(default_factory=dict)
    results: dict[int, CubicationResult] = field(default_factory=dict)
    split_plans: dict[int, list[CubicationSplitPlan]] = field(default_factory=dict)
    split_plan_items: dict[int, list[CubicationSplitPlanItem]] = field(default_factory=dict)

    next_run_id: int = 1
    next_result_id: int = 1

    def create_run(self, order_id: int) -> CubicationRun:
        run = CubicationRun(run_id=self.next_run_id, order_id=order_id)
        self.runs[self.next_run_id] = run
        self.next_run_id += 1
        return run

    def save_run_items(self, run_id: int, items: list[CubicationRunItem]) -> None:
        self.run_items[run_id] = items

    def save_candidates(self, run_id: int, candidates: list[CandidateEvaluation]) -> None:
        self.candidates[run_id] = candidates

    def save_result(self, run_id: int, status: str, recommended_truck_type_id: int | None, notes: str | None = None) -> CubicationResult:
        result = CubicationResult(
            result_id=self.next_result_id,
            run_id=run_id,
            status=status,
            recommended_truck_type_id=recommended_truck_type_id,
            notes=notes,
        )
        self.results[run_id] = result
        self.next_result_id += 1
        return result

    def save_split_plan(self, run_id: int, plans: list[CubicationSplitPlan], items: list[CubicationSplitPlanItem]) -> None:
        self.split_plans[run_id] = plans
        self.split_plan_items[run_id] = items
