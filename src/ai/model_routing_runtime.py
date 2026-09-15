"""Runtime bridge between model observation, role policy, and routing."""
from __future__ import annotations

from typing import Iterable

from src.ai.model_catalog import ModelCatalog
from src.ai.model_role_policy import ModelRolePolicy
from src.ai.model_routing import ModelProfile, ModelRole, ModelRouter, RoutingDecision, RoutingRequest


class ModelRoutingRuntime:
    """Own the deterministic observation → role policy → routing lifecycle."""

    def __init__(self, policy: ModelRolePolicy) -> None:
        if not isinstance(policy, ModelRolePolicy):
            raise TypeError("policy must be a ModelRolePolicy")
        self._policy = policy
        self._catalog = ModelCatalog(
            rule.profile(available=False) for rule in policy.list_rules()
        )
        self._router = self._catalog.router()

    @property
    def catalog(self) -> ModelCatalog:
        return self._catalog

    @property
    def policy(self) -> ModelRolePolicy:
        return self._policy

    def observe_models(self, model_ids: Iterable[str]) -> None:
        """Refresh availability from a provider observation snapshot."""
        self._catalog.observe_ids(model_ids)
        self._router = self._catalog.router()

    def observe_openai_models(self, payload) -> tuple[str, ...]:
        """Refresh availability from an OpenAI-compatible /v1/models payload."""
        observed = self._catalog.observe_openai_models(payload)
        self._router = self._catalog.router()
        return observed

    def list_models(self) -> tuple[ModelProfile, ...]:
        return self._catalog.profiles()

    def observed_model_ids(self) -> tuple[str, ...]:
        return self._catalog.observed_model_ids()

    def route(self, role: ModelRole, preferred_model: str | None = None) -> RoutingDecision:
        return self._router.route(
            RoutingRequest(role=role, preferred_model=preferred_model)
        )
