"""M23.32: explicit verification evidence for rollback repair application.

This boundary verifies that an applied repair result matches the expected
world-model state without mutating source artifacts or claiming truth.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model import EnvironmentWorldModel
from src.core.environment_world_model_rollback_repair_application import (
    EnvironmentWorldModelRollbackRepairApplication,
)


class EnvironmentWorldModelRollbackRepairVerificationError(RuntimeError):
    """Raised when rollback-repair verification cannot be completed safely."""


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
class EnvironmentWorldModelRollbackRepairVerification:
    """Immutable evidence describing one rollback-repair verification result."""

    verification_id: str
    environment_id: str
    application_id: str
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


class EnvironmentWorldModelRollbackRepairVerificationService:
    """Verify an M23.31 repair application against an observed current model."""

    def verify(
        self,
        application: EnvironmentWorldModelRollbackRepairApplication,
        observed_model: EnvironmentWorldModel,
        *,
        verification_id: str,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairVerification:
        if type(application) is not EnvironmentWorldModelRollbackRepairApplication:
            raise TypeError(
                "application must be EnvironmentWorldModelRollbackRepairApplication"
            )
        if type(observed_model) is not EnvironmentWorldModel:
            raise TypeError("observed_model must be EnvironmentWorldModel")

        if application.environment_id != observed_model.environment_id:
            raise EnvironmentWorldModelRollbackRepairVerificationError(
                "application and observed model environments must match"
            )

        expected_model_id = application.resulting_model_id
        observed_model_id = observed_model.model_id

        verified = (
            application.applied
            and expected_model_id == observed_model_id
        )
        default_reason = (
            "applied repair result matches observed current model"
            if verified
            else "observed current model does not match applied repair result"
        )

        return EnvironmentWorldModelRollbackRepairVerification(
            verification_id=verification_id,
            environment_id=application.environment_id,
            application_id=application.application_id,
            expected_model_id=expected_model_id,
            observed_model_id=observed_model_id,
            verified=verified,
            reasons=reasons or {"status": default_reason},
            lineage=lineage
            or {
                "application_id": application.application_id,
                "expected_model_id": expected_model_id,
                "observed_model_id": observed_model_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairVerification",
    "EnvironmentWorldModelRollbackRepairVerificationError",
    "EnvironmentWorldModelRollbackRepairVerificationService",
]
