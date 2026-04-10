from __future__ import annotations

from math import ceil

from .models import CargoItem, ContainerSpec, CubicationResult


DEFAULT_CONTAINER_CATALOG = [
    ContainerSpec("LTL_SMALL_VAN", 220, 140, 140, 900),
    ContainerSpec("LTL_MEDIUM_TRUCK", 420, 200, 200, 2500),
    ContainerSpec("FTL_20FT", 590, 235, 239, 28200),
    ContainerSpec("FTL_40FT", 1203, 235, 239, 26600),
]


def _item_volume_cm3(item: CargoItem) -> float:
    return item.length_cm * item.width_cm * item.height_cm * item.quantity


def evaluate_cubication(
    items: list[CargoItem],
    containers: list[ContainerSpec] | None = None,
    safety_buffer_ratio: float = 0.1,
) -> CubicationResult:
    if not items:
        raise ValueError("items cannot be empty")

    catalog = containers or DEFAULT_CONTAINER_CATALOG
    total_volume = sum(_item_volume_cm3(item) for item in items)
    total_weight = sum(item.weight_kg * item.quantity for item in items)

    sorted_catalog = sorted(catalog, key=lambda c: c.volume_cm3)
    for container in sorted_catalog:
        effective_volume = container.volume_cm3 * (1 - safety_buffer_ratio)
        if total_volume <= effective_volume and total_weight <= container.max_payload_kg:
            utilized_ratio = total_volume / container.volume_cm3
            return CubicationResult(
                total_item_volume_cm3=total_volume,
                total_weight_kg=total_weight,
                utilized_volume_ratio=round(utilized_ratio, 4),
                estimated_container_fill=ceil(utilized_ratio * 100),
                recommended_container=container.code,
            )

    largest = sorted_catalog[-1]
    utilized_ratio = total_volume / largest.volume_cm3
    return CubicationResult(
        total_item_volume_cm3=total_volume,
        total_weight_kg=total_weight,
        utilized_volume_ratio=round(utilized_ratio, 4),
        estimated_container_fill=ceil(utilized_ratio * 100),
        recommended_container=f"MULTI_{largest.code}",
    )
