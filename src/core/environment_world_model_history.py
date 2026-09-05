"""M23.21: immutable historical retention for world-model artifacts.

History preserves prior descriptive models without changing current-model selection,
truth, authority, or execution semantics.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model import EnvironmentWorldModel


class EnvironmentWorldModelHistoryError(RuntimeError):
    """Raised when world-model history cannot be updated safely."""


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze(item) for item in value)
    return value


@dataclass(frozen=True)
class EnvironmentWorldModelHistory:
    """Immutable ordered history of descriptive world-model artifacts for one environment."""

    environment_id: str
    models: tuple[EnvironmentWorldModel, ...]
    lineage: Mapping[str, Any] = MappingProxyType({})

    def __post_init__(self) -> None:
        if not isinstance(self.environment_id, str) or not self.environment_id.strip():
            raise ValueError("environment_id must be a non-empty string")
        if not isinstance(self.models, tuple):
            raise TypeError("models must be a tuple")
        seen: set[str] = set()
        for model in self.models:
            if type(model) is not EnvironmentWorldModel:
                raise TypeError("history models must be EnvironmentWorldModel instances")
            if model.environment_id != self.environment_id:
                raise EnvironmentWorldModelHistoryError(
                    "history model environment identity does not match history scope"
                )
            if model.model_id in seen:
                raise EnvironmentWorldModelHistoryError("history model identities must be unique")
            seen.add(model.model_id)
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "models", tuple(self.models))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def model_ids(self) -> tuple[str, ...]:
        return tuple(model.model_id for model in self.models)

    @property
    def latest(self) -> EnvironmentWorldModel | None:
        return self.models[-1] if self.models else None


class EnvironmentWorldModelHistoryService:
    """Append descriptive world-model artifacts without mutating prior history."""

    def append(
        self,
        history: EnvironmentWorldModelHistory | None,
        model: EnvironmentWorldModel,
        *,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelHistory:
        if history is not None and type(history) is not EnvironmentWorldModelHistory:
            raise TypeError("history must be EnvironmentWorldModelHistory or None")
        if type(model) is not EnvironmentWorldModel:
            raise TypeError("model must be EnvironmentWorldModel")

        if history is None:
            models: tuple[EnvironmentWorldModel, ...] = (model,)
            environment_id = model.environment_id
        else:
            if history.environment_id != model.environment_id:
                raise EnvironmentWorldModelHistoryError(
                    "history and model must share an environment"
                )
            if model.model_id in history.model_ids:
                raise EnvironmentWorldModelHistoryError(
                    "model identity already exists in history"
                )
            models = (*history.models, model)
            environment_id = history.environment_id

        return EnvironmentWorldModelHistory(
            environment_id=environment_id,
            models=models,
            lineage=lineage or {
                "previous_model_id": history.latest.model_id if history and history.latest else None,
                "appended_model_id": model.model_id,
            },
        )
