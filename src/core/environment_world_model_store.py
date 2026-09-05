"""M23.19: provider-neutral storage contract for the current world model.

This boundary isolates state retention behind an explicit store contract.
It does not imply durability, persistence technology, synchronization, or truth.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.core.environment_world_model import EnvironmentWorldModel


class EnvironmentWorldModelStoreError(RuntimeError):
    """Raised when a world-model store operation cannot be completed safely."""


class EnvironmentWorldModelStore(Protocol):
    """Provider-neutral contract for retaining the current world model per environment."""

    def get(self, environment_id: str) -> EnvironmentWorldModel | None:
        """Return the current model for an environment, or ``None`` when absent."""

    def put(
        self,
        model: EnvironmentWorldModel,
        *,
        expected_model_id: str | None = None,
    ) -> EnvironmentWorldModel:
        """Store a model, optionally requiring an expected current model identity."""

    def remove(self, environment_id: str) -> EnvironmentWorldModel | None:
        """Remove and return the current model for an environment."""


@dataclass
class InMemoryEnvironmentWorldModelStore:
    """Reference store used to prove the contract without choosing persistence technology."""

    _models: dict[str, EnvironmentWorldModel] | None = None

    def __post_init__(self) -> None:
        if self._models is None:
            self._models = {}
        elif not isinstance(self._models, dict):
            raise TypeError("_models must be a dict")
        else:
            for environment_id, model in self._models.items():
                self._validate_environment_id(environment_id)
                self._validate_model(model)
                if model.environment_id != environment_id:
                    raise EnvironmentWorldModelStoreError(
                        "stored model environment identity does not match store key"
                    )

    @staticmethod
    def _validate_environment_id(environment_id: str) -> None:
        if not isinstance(environment_id, str) or not environment_id.strip():
            raise ValueError("environment_id must be a non-empty string")

    @staticmethod
    def _validate_model(model: EnvironmentWorldModel) -> None:
        if type(model) is not EnvironmentWorldModel:
            raise TypeError("model must be EnvironmentWorldModel")

    def get(self, environment_id: str) -> EnvironmentWorldModel | None:
        self._validate_environment_id(environment_id)
        return self._models.get(environment_id)

    def put(
        self,
        model: EnvironmentWorldModel,
        *,
        expected_model_id: str | None = None,
    ) -> EnvironmentWorldModel:
        self._validate_model(model)
        current = self._models.get(model.environment_id)
        if expected_model_id is not None:
            if not isinstance(expected_model_id, str) or not expected_model_id.strip():
                raise ValueError("expected_model_id must be a non-empty string when provided")
            if current is None:
                raise EnvironmentWorldModelStoreError(
                    "expected current model is absent"
                )
            if current.model_id != expected_model_id:
                raise EnvironmentWorldModelStoreError(
                    "expected current model identity does not match stored model"
                )
        self._models[model.environment_id] = model
        return model

    def remove(self, environment_id: str) -> EnvironmentWorldModel | None:
        self._validate_environment_id(environment_id)
        return self._models.pop(environment_id, None)
