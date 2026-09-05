"""M23.26: explicit persistence coordination for world-model rollback.

This boundary persists the immutable result produced by rollback application into
an existing current-model store. It uses the store's compare-and-swap guard and
does not mutate history or introduce transaction/synchronization semantics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model import EnvironmentWorldModel
from src.core.environment_world_model_rollback_application import (
    EnvironmentWorldModelRollbackApplication,
)
from src.core.environment_world_model_store import EnvironmentWorldModelStore


class EnvironmentWorldModelRollbackPersistenceError(RuntimeError):
    """Raised when rollback persistence cannot be completed safely."""


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
class EnvironmentWorldModelRollbackPersistence:
    """Immutable record of one rollback persistence operation."""

    persistence_id: str
    environment_id: str
    application_id: str
    previous_model_id: str
    resulting_model_id: str
    persisted: bool
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "persistence_id",
            "environment_id",
            "application_id",
            "previous_model_id",
            "resulting_model_id",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.persisted and not self.resulting_model_id:
            raise ValueError("persisted result must have a resulting model identity")
        if not isinstance(self.reasons, Mapping):
            raise TypeError("reasons must be a mapping")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def mutates_history(self) -> bool:
        return False

    @property
    def is_authorization(self) -> bool:
        return False


class EnvironmentWorldModelRollbackPersistenceService:
    """Persist an M23.25 rollback result into the current-model store."""

    def persist(
        self,
        application: EnvironmentWorldModelRollbackApplication,
        resulting_model: EnvironmentWorldModel,
        store: EnvironmentWorldModelStore,
        *,
        persistence_id: str,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackPersistence:
        if type(application) is not EnvironmentWorldModelRollbackApplication:
            raise TypeError("application must be EnvironmentWorldModelRollbackApplication")
        if type(resulting_model) is not EnvironmentWorldModel:
            raise TypeError("resulting_model must be EnvironmentWorldModel")
        if not hasattr(store, "get") or not hasattr(store, "put"):
            raise TypeError("store must implement the EnvironmentWorldModelStore contract")

        if application.environment_id != resulting_model.environment_id:
            raise EnvironmentWorldModelRollbackPersistenceError(
                "application and resulting model environments must match"
            )
        if application.resulting_model_id != resulting_model.model_id:
            raise EnvironmentWorldModelRollbackPersistenceError(
                "application resulting identity does not match resulting model"
            )

        current = store.get(application.environment_id)
        if current is None:
            raise EnvironmentWorldModelRollbackPersistenceError(
                "current model is absent from store"
            )
        if current.environment_id != application.environment_id:
            raise EnvironmentWorldModelRollbackPersistenceError(
                "stored current model environment does not match application"
            )
        if current.model_id != application.previous_model_id:
            raise EnvironmentWorldModelRollbackPersistenceError(
                "stored current model identity does not match application previous model"
            )

        if not application.applied:
            return EnvironmentWorldModelRollbackPersistence(
                persistence_id=persistence_id,
                environment_id=application.environment_id,
                application_id=application.application_id,
                previous_model_id=application.previous_model_id,
                resulting_model_id=application.resulting_model_id,
                persisted=False,
                reasons=reasons or {"status": "rollback application was not applied; store unchanged"},
                lineage=lineage or {
                    "application_id": application.application_id,
                    "previous_model_id": application.previous_model_id,
                    "resulting_model_id": application.resulting_model_id,
                },
            )

        try:
            store.put(resulting_model, expected_model_id=application.previous_model_id)
        except Exception as exc:
            raise EnvironmentWorldModelRollbackPersistenceError(
                "rollback result could not be persisted with expected current-model identity"
            ) from exc

        return EnvironmentWorldModelRollbackPersistence(
            persistence_id=persistence_id,
            environment_id=application.environment_id,
            application_id=application.application_id,
            previous_model_id=application.previous_model_id,
            resulting_model_id=application.resulting_model_id,
            persisted=True,
            reasons=reasons or {"status": "accepted rollback result persisted as current model"},
            lineage=lineage or {
                "application_id": application.application_id,
                "previous_model_id": application.previous_model_id,
                "resulting_model_id": application.resulting_model_id,
            },
        )
