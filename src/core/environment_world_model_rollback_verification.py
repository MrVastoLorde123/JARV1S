"""M23.27: explicit verification evidence for persisted world-model rollback.

This boundary verifies that a persisted current model matches the accepted
rollback application result without mutating source artifacts or claiming truth.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model import EnvironmentWorldModel
from src.core.environment_world_model_rollback_application import (
    EnvironmentWorldModelRollbackApplication,
)
from src.core.environment_world_model_rollback_persistence import (
    EnvironmentWorldModelRollbackPersistence,
)


class EnvironmentWorldModelRollbackVerificationError(RuntimeError):
    """Raised when rollback verification cannot be completed safely."""


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
class EnvironmentWorldModelRollbackVerification:
    """Immutable evidence describing one rollback verification result."""

    verification_id: str
    environment_id: str
    application_id: str
    persistence_id: str
    expected_model_id: str
    observed_model_id: str
    verified: bool
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "verification_id",
            "environment_id",
            "application_id",
            "persistence_id",
            "expected_model_id",
            "observed_model_id",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.verified, bool):
            raise TypeError("verified must be a bool")
        if not isinstance(self.reasons, Mapping):
            raise TypeError("reasons must be a mapping")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def establishes_truth(self) -> bool:
        return False

    @property
    def is_authorization(self) -> bool:
        return False


class EnvironmentWorldModelRollbackVerificationService:
    """Verify an M23.26 persistence result against the observed current model."""

    def verify(
        self,
        application: EnvironmentWorldModelRollbackApplication,
        persistence: EnvironmentWorldModelRollbackPersistence,
        observed_model: EnvironmentWorldModel,
        *,
        verification_id: str,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackVerification:
        if type(application) is not EnvironmentWorldModelRollbackApplication:
            raise TypeError("application must be EnvironmentWorldModelRollbackApplication")
        if type(persistence) is not EnvironmentWorldModelRollbackPersistence:
            raise TypeError("persistence must be EnvironmentWorldModelRollbackPersistence")
        if type(observed_model) is not EnvironmentWorldModel:
            raise TypeError("observed_model must be EnvironmentWorldModel")

        if application.environment_id != persistence.environment_id:
            raise EnvironmentWorldModelRollbackVerificationError(
                "application and persistence environments must match"
            )
        if application.application_id != persistence.application_id:
            raise EnvironmentWorldModelRollbackVerificationError(
                "application identity does not match persistence"
            )
        if application.resulting_model_id != persistence.resulting_model_id:
            raise EnvironmentWorldModelRollbackVerificationError(
                "application and persistence resulting identities must match"
            )
        if observed_model.environment_id != persistence.environment_id:
            raise EnvironmentWorldModelRollbackVerificationError(
                "observed model environment does not match persistence"
            )

        expected_model_id = persistence.resulting_model_id
        observed_model_id = observed_model.model_id
        verified = persistence.persisted and observed_model_id == expected_model_id

        default_reason = (
            "persisted rollback result matches observed current model"
            if verified
            else "observed current model does not match persisted rollback result"
        )

        return EnvironmentWorldModelRollbackVerification(
            verification_id=verification_id,
            environment_id=persistence.environment_id,
            application_id=persistence.application_id,
            persistence_id=persistence.persistence_id,
            expected_model_id=expected_model_id,
            observed_model_id=observed_model_id,
            verified=verified,
            reasons=reasons or {"status": default_reason},
            lineage=lineage or {
                "application_id": application.application_id,
                "persistence_id": persistence.persistence_id,
                "expected_model_id": expected_model_id,
                "observed_model_id": observed_model_id,
            },
        )
