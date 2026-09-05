"""M23.33: explicit decision evidence for rollback-repair verification."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_verification import (
    EnvironmentWorldModelRollbackRepairVerification,
)


class EnvironmentWorldModelRollbackRepairVerificationDecisionError(RuntimeError):
    """Raised when a repair-verification decision cannot be formed safely."""


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
class EnvironmentWorldModelRollbackRepairVerificationDecision:
    """Immutable decision evidence derived from one repair-verification result."""

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
    def authorizes_follow_up(self) -> bool:
        return False


class EnvironmentWorldModelRollbackRepairVerificationDecisionService:
    """Convert repair-verification evidence into deterministic decision evidence."""

    def decide(
        self,
        verification: EnvironmentWorldModelRollbackRepairVerification,
        *,
        decision_id: str,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairVerificationDecision:
        if type(verification) is not EnvironmentWorldModelRollbackRepairVerification:
            raise TypeError(
                "verification must be EnvironmentWorldModelRollbackRepairVerification"
            )

        if verification.verified:
            decision = "ACCEPT"
            default_reason = "rollback repair verification matched the expected model"
        else:
            decision = "REJECT"
            default_reason = "rollback repair verification did not establish the expected model"

        return EnvironmentWorldModelRollbackRepairVerificationDecision(
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
    "EnvironmentWorldModelRollbackRepairVerificationDecision",
    "EnvironmentWorldModelRollbackRepairVerificationDecisionError",
    "EnvironmentWorldModelRollbackRepairVerificationDecisionService",
]
