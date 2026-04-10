from __future__ import annotations


class StackRuleResolver:
    """Resolve stack-layer rules with a safe default for manual review flows."""

    def __init__(self, default_max_stack_layer: int = 1) -> None:
        self.default_max_stack_layer = max(default_max_stack_layer, 1)

    def resolve_max_stack_layer(self, explicit_max_stack_layer: int | None) -> tuple[int, bool]:
        if explicit_max_stack_layer and explicit_max_stack_layer > 0:
            return explicit_max_stack_layer, False
        return self.default_max_stack_layer, True
