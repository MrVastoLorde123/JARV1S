"""Runtime-owned observation catalog for locally available AI models."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from src.ai.model_routing import ModelProfile, ModelRole, ModelRouter


@dataclass(frozen=True)
class ModelObservation:
    model_id: str
    observed: bool = True
    metadata: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.model_id, str) or not self.model_id.strip():
            raise ValueError("model_id cannot be empty")


class ModelCatalog:
    """Maintain observed model availability without granting model authority."""

    def __init__(self, profiles: Iterable[ModelProfile] = ()) -> None:
        self._profiles: dict[str, ModelProfile] = {}
        self._observations: dict[str, ModelObservation] = {}
        for profile in profiles:
            self.register_profile(profile)

    def register_profile(self, profile: ModelProfile) -> None:
        if not isinstance(profile, ModelProfile):
            raise TypeError("profile must be a ModelProfile")
        existing = self._profiles.get(profile.model_id)
        if existing is not None and existing != profile:
            raise ValueError(f"conflicting profile for model_id: {profile.model_id}")
        self._profiles[profile.model_id] = profile

    def observe(self, observation: ModelObservation) -> None:
        if not isinstance(observation, ModelObservation):
            raise TypeError("observation must be a ModelObservation")
        self._observations[observation.model_id] = observation

    def observe_ids(self, model_ids: Iterable[str]) -> None:
        """Replace the latest provider observation without inventing profiles."""
        seen = {
            model_id
            for model_id in model_ids
            if isinstance(model_id, str) and model_id.strip()
        }
        self._observations = {
            model_id: ModelObservation(model_id=model_id, observed=True)
            for model_id in seen
        }
        for model_id in self._profiles:
            if model_id not in seen:
                self._observations[model_id] = ModelObservation(
                    model_id=model_id,
                    observed=False,
                )

    def observe_openai_models(self, payload: Mapping[str, Any]) -> tuple[str, ...]:
        """Observe IDs from an OpenAI-compatible /v1/models response."""
        if not isinstance(payload, Mapping):
            raise TypeError("/v1/models payload must be a mapping")
        raw_models = payload.get("data", ())
        if not isinstance(raw_models, (list, tuple)):
            raise ValueError("/v1/models payload field 'data' must be a sequence")
        model_ids: list[str] = []
        for item in raw_models:
            if isinstance(item, Mapping):
                model_id = item.get("id")
                if isinstance(model_id, str) and model_id.strip():
                    model_ids.append(model_id)
        self.observe_ids(model_ids)
        return tuple(model_ids)

    def profile(self, model_id: str) -> ModelProfile:
        try:
            base = self._profiles[model_id]
        except KeyError as exc:
            raise KeyError(f"unknown model: {model_id}") from exc
        observation = self._observations.get(model_id)
        if observation is None:
            return base
        return ModelProfile(
            model_id=base.model_id,
            roles=base.roles,
            priority=base.priority,
            available=observation.observed,
            notes=base.notes,
        )

    def profiles(self) -> tuple[ModelProfile, ...]:
        return tuple(self.profile(model_id) for model_id in self._profiles)

    def router(self) -> ModelRouter:
        """Build a deterministic router from the latest observed profiles."""
        return ModelRouter(self.profiles())

    def observed_model_ids(self) -> tuple[str, ...]:
        return tuple(
            sorted(
                model_id
                for model_id, item in self._observations.items()
                if item.observed
            )
        )

    @staticmethod
    def roles_for(*roles: ModelRole) -> frozenset[ModelRole]:
        if not all(isinstance(role, ModelRole) for role in roles):
            raise TypeError("roles must contain only ModelRole values")
        return frozenset(roles)
