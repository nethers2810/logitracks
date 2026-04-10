from __future__ import annotations

from engine.models import CustomerConstraint, LaneRule, OrderItem, TruckType
from engine.repository import InMemoryRepository
from engine.services.recommendation_service import RecommendationService


class EngineAPI:
    """Lightweight API facade for Stage 3 endpoint contracts."""

    def __init__(self, recommendation_service: RecommendationService, repository: InMemoryRepository) -> None:
        self.recommendation_service = recommendation_service
        self.repository = repository

    # POST /api/engine/runs/{order_id}
    def create_run(
        self,
        order_id: int,
        order_items: list[OrderItem],
        trucks: list[TruckType],
        customer_constraint: CustomerConstraint | None = None,
        lane_rules: list[LaneRule] | None = None,
    ) -> dict:
        run_id = self.recommendation_service.run(order_id, order_items, trucks, customer_constraint, lane_rules)
        return {"run_id": run_id}

    # GET /api/engine/runs/{run_id}
    def get_run(self, run_id: int) -> dict:
        run = self.repository.runs[run_id]
        return {"run_id": run.run_id, "order_id": run.order_id, "created_at": run.created_at.isoformat()}

    # GET /api/engine/runs/{run_id}/candidates
    def get_candidates(self, run_id: int) -> list[dict]:
        return [c.__dict__ for c in self.repository.candidates.get(run_id, [])]

    # GET /api/engine/runs/{run_id}/result
    def get_result(self, run_id: int) -> dict:
        return self.repository.results[run_id].__dict__

    # GET /api/engine/runs/{run_id}/split-plan
    def get_split_plan(self, run_id: int) -> dict:
        return {
            "plans": [x.__dict__ for x in self.repository.split_plans.get(run_id, [])],
            "items": [x.__dict__ for x in self.repository.split_plan_items.get(run_id, [])],
        }


def build_api() -> EngineAPI:
    repository = InMemoryRepository()
    service = RecommendationService(repository)
    return EngineAPI(service, repository)
