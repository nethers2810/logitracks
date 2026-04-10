from dataclasses import dataclass
from typing import Literal


CargoType = Literal["box", "cylinder", "irregular"]


@dataclass(frozen=True)
class CargoItem:
    sku: str
    cargo_type: CargoType
    length_cm: float
    width_cm: float
    height_cm: float
    quantity: int
    weight_kg: float


@dataclass(frozen=True)
class ContainerSpec:
    code: str
    internal_length_cm: float
    internal_width_cm: float
    internal_height_cm: float
    max_payload_kg: float

    @property
    def volume_cm3(self) -> float:
        return self.internal_length_cm * self.internal_width_cm * self.internal_height_cm


@dataclass(frozen=True)
class CubicationResult:
    total_item_volume_cm3: float
    total_weight_kg: float
    utilized_volume_ratio: float
    estimated_container_fill: int
    recommended_container: str
