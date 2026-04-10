from engine.models import LaneRule, OrderItem, TruckType
from engine.repository import InMemoryRepository
from engine.services.cubication_calculator import CubicationCalculator
from engine.services.recommendation_service import RecommendationService
from engine.services.truck_candidate_evaluator import TruckCandidateEvaluator


def test_stack_count_calculation():
    calc = CubicationCalculator()
    item = OrderItem(
        order_item_id=1,
        sap_delivery_qty=10,
        sap_total_weight_kg=100,
        sap_total_volume_m3=2,
        max_stack_layer=4,
        length_mm=1000,
        width_mm=1000,
        height_mm=500,
    )

    run_item, _ = calc.build_run_item(run_id=1, run_item_id=1, item=item)

    assert run_item.stack_count == 3
    assert run_item.stack_count_est == 3


def test_fallback_calculation_without_dimensions():
    calc = CubicationCalculator()
    item = OrderItem(
        order_item_id=2,
        sap_delivery_qty=5,
        sap_total_weight_kg=50,
        sap_total_volume_m3=1,
        max_stack_layer=2,
    )

    run_item, assumed = calc.build_run_item(run_id=1, run_item_id=1, item=item)

    assert run_item.required_floor_area_m2 is None
    assert run_item.required_height_mm is None
    assert assumed is True


def test_truck_pass_fail_evaluation():
    calc = CubicationCalculator()
    evaluator = TruckCandidateEvaluator(odol_safety_factor=1.0)

    run_item, _ = calc.build_run_item(
        run_id=1,
        run_item_id=1,
        item=OrderItem(
            order_item_id=3,
            sap_delivery_qty=10,
            sap_total_weight_kg=1000,
            sap_total_volume_m3=10,
            max_stack_layer=2,
            length_mm=1000,
            width_mm=1000,
            height_mm=1000,
        ),
    )

    trucks = [
        TruckType(truck_type_id=1, name="Small", max_payload_kg=500, cargo_volume_m3=8, deck_area_m2=8, internal_height_mm=2000),
        TruckType(truck_type_id=2, name="Large", max_payload_kg=2000, cargo_volume_m3=20, deck_area_m2=20, internal_height_mm=3000),
    ]

    candidates = evaluator.evaluate(1, evaluator.aggregate([run_item]), trucks, None, [LaneRule(truck_type_id=2, priority_no=1)])

    small = [c for c in candidates if c.truck_type_id == 1][0]
    large = [c for c in candidates if c.truck_type_id == 2][0]

    assert small.pass_weight is False
    assert large.score is not None
    assert large.rank_no == 1


def test_split_recommendation_generation():
    repository = InMemoryRepository()
    service = RecommendationService(repository)

    run_id = service.run(
        order_id=99,
        order_items=[
            OrderItem(order_item_id=10, sap_delivery_qty=20, sap_total_weight_kg=6000, sap_total_volume_m3=60, max_stack_layer=1),
        ],
        trucks=[
            TruckType(truck_type_id=1, name="Medium", max_payload_kg=2000, cargo_volume_m3=25),
        ],
    )

    result = repository.results[run_id]
    assert result.status == "split_recommendation"
    assert len(repository.split_plans[run_id]) >= 2
