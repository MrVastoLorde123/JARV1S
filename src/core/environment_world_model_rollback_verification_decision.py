"""M23.28: explicit decision evidence for world-model rollback verification."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_verification import (
    EnvironmentWorldModelRollbackVerification,
)


class EnvironmentWorldModelRollbackVerificationDecisionError(RuntimeError):
    """Raised when a rollback verification decision cannot be formed safely."""


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
class EnvironmentWorldModelRollbackVerificationDecision:
    """Immutable decision evidence derived from one rollback verification result."""

    decision_id: str
    environment_id: str
    verification_id: str
    expected_model_id: str
    observed_model_id: str
    decision: str
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "decision_id",
            "environment_id",
            "verification_id",
            "expected_model_id",
            "observed_model_id",
            "decision",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.decision not in {"ACCEPT", "REJECT", "DEFER"}:
            raise ValueError("decision must be ACCEPT, REJECT, or DEFER")
        if not isinstance(self.reasons, Mapping):
            raise TypeError("reasons must be a mapping")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_advisory_only(self) -> bool:
        return True

    @property
    def authorizes_repair(self) -> bool:
        return False


class EnvironmentWorldModelRollbackVerificationDecisionService:
    """Convert rollback verification evidence into deterministic decision evidence."""

    def decide(
        self,
        verification: EnvironmentWorldModelRollbackVerification,
        *,
        decision_id: str,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackVerificationDecision:
        if type(verification) is not EnvironmentWorldModelRollbackVerification:
            raise TypeError(
                "verification must be EnvironmentWorldModelRollbackVerification"
            )

        if verification.verified:
            decision = "ACCEPT"
            default_reason = "rollback verification matched the expected persisted model"
        else:
            decision = "REJECT"
            default_reason = "rollback verification did not establish the expected persisted model"

        return EnvironmentWorldModelRollbackVerificationDecision(
            decision_id=decision_id,
            environment_id=verification.environment_id,
            verification_id=verification.verification_id,
            expected_model_id=verification.expected_model_id,
            observed_model_id=verification.observed_model_id,
            decision=decision,
            reasons=reasons or {"status": default_reason},
            lineage=lineage
            or {
                "verification_id": verification.verification_id,
                "expected_model_id": verification.expected_model_id,
                "observed_model_id": verification.observed_model_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackVerificationDecision",
    "EnvironmentWorldModelRollbackVerificationDecisionError",
    "EnvironmentWorldModelRollbackVerificationDecisionService",
]
