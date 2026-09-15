"""Declarative model-role fitness policy for JARVIS.

The policy assigns cognitive roles to explicitly identified models. It does
not discover models, execute requests, or grant authority. Availability remains
an observation owned by ModelCatalog.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from src.ai.model_routing import ModelProfile, ModelRole


@dataclass(frozen=True)
class ModelRolePolicyRule:
    """Explicit role-fitness rule for one model identifier."""

    model_id: str
    roles: frozenset[ModelRole]
    priority: int = 0
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.model_id.strip():
            raise ValueError("model_id cannot be empty")
        if not self.roles:
            raise ValueError("roles cannot be empty")
        if self.priority < 0:
            raise ValueError("priority cannot be negative")

    def profile(self, *, available: bool = False) -> ModelProfile:
        """Build a routing profile while keeping availability explicit."""
        return ModelProfile(
            model_id=self.model_id,
            roles=self.roles,
            priority=self.priority,
            available=available,
            notes=self.notes,
        )


class ModelRolePolicy:
    """Deterministic registry of explicit model role-fitness rules."""

    def __init__(self, rules: Iterable[ModelRolePolicyRule] = ()) -> None:
        self._rules: dict[str, ModelRolePolicyRule] = {}
        for rule in rules:
            self.register(rule)

    def register(self, rule: ModelRolePolicyRule) -> None:
        if not isinstance(rule, ModelRolePolicyRule):
            raise TypeError("rule must be a ModelRolePolicyRule")
        if rule.model_id in self._rules:
            raise ValueError(f"duplicate model_id: {rule.model_id}")
        self._rules[rule.model_id] = rule

    def rule(self, model_id: str) -> ModelRolePolicyRule:
        try:
            return self._rules[model_id]
        except KeyError as exc:
            raise KeyError(f"no role policy for model: {model_id}") from exc

    def list_rules(self) -> tuple[ModelRolePolicyRule, ...]:
        return tuple(self._rules.values())

    def profiles_for_observed(self, model_ids: Iterable[str]) -> tuple[ModelProfile, ...]:
        """Return profiles only for observed IDs with explicit role policy."""
        observed = {
            model_id
            for model_id in model_ids
            if isinstance(model_id, str) and model_id.strip()
        }
        return tuple(
            self._rules[model_id].profile(available=True)
            for model_id in sorted(observed)
            if model_id in self._rules
        )
