"""M23.60: learning eligibility boundary for verified v2 learning signals."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_learning_signal_integrity_v2 import (
    EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2,
    EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_learning_signal_v2 import (
    EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Status,
)


class EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Error(RuntimeError):
    """Raised when learning eligibility evidence cannot be formed safely."""


class EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    INELIGIBLE = "INELIGIBLE"


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
class EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2:
    """Immutable advisory evidence that a verified learning signal may be considered for adaptation."""

    eligibility_id: str
    integrity_id: str
    signal_id: str
    evaluation_id: str
    feedback_id: str
    outcome_id: str
    execution_id: str
    preparation_id: str
    decision_id: str
    proposal_id: str
    assessment_id: str | None
    environment_id: str
    expected_model_id: str
    observed_model_id: str
    signal_integrity_status: EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2Status
    signal_status: EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Status
    confidence: float
    signal_fingerprint: str
    eligibility_status: EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "eligibility_id", "integrity_id", "signal_id", "evaluation_id", "feedback_id",
            "outcome_id", "execution_id", "preparation_id", "decision_id", "proposal_id",
            "environment_id", "expected_model_id", "observed_model_id", "signal_fingerprint",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.assessment_id is not None and (
            not isinstance(self.assessment_id, str) or not self.assessment_id.strip()
        ):
            raise ValueError("assessment_id must be None or a non-empty string")
        if not isinstance(
            self.signal_integrity_status,
            EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2Status,
        ):
            raise TypeError("signal_integrity_status must be a learning-signal integrity v2 status")
        if not isinstance(self.signal_status, EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Status):
            raise TypeError("signal_status must be a learning-signal v2 status")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)):
            raise ValueError("confidence must be numeric")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if not isinstance(
            self.eligibility_status,
            EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status,
        ):
            raise TypeError("eligibility_status must be a learning-eligibility v2 status")
        if self.eligibility_status == EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status.ELIGIBLE:
            if self.signal_integrity_status != EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2Status.VALID:
                raise ValueError("ELIGIBLE requires VALID signal integrity")
            if len(self.signal_fingerprint) != 64:
                raise ValueError("ELIGIBLE requires a SHA-256 signal fingerprint")
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
    def permits_adaptation(self) -> bool:
        return False

    @property
    def requests_adaptation(self) -> bool:
        return False

    @property
    def grants_authority(self) -> bool:
        return False

    @property
    def updates_model(self) -> bool:
        return False

    @property
    def mutates_memory(self) -> bool:
        return False

    @property
    def mutates_policy(self) -> bool:
        return False

    @property
    def mutates_persistence(self) -> bool:
        return False

    @property
    def schedules_work(self) -> bool:
        return False


class EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Service:
    """Determine whether one valid learning signal is eligible for future consideration only."""

    def evaluate(
        self,
        integrity: EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2,
        *,
        eligibility_id: str,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2:
        if type(integrity) is not EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2:
            raise TypeError(
                "integrity must be EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2"
            )
        if not isinstance(eligibility_id, str) or not eligibility_id.strip():
            raise ValueError("eligibility_id must be a non-empty string")

        if integrity.status == EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2Status.VALID:
            eligibility_status = EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status.ELIGIBLE
            default_reason = "verified learning-signal integrity is eligible for future adaptation consideration"
        elif integrity.status == EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2Status.INVALID:
            eligibility_status = EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status.INELIGIBLE
            default_reason = "learning-signal integrity is invalid; learning consideration is blocked"
        else:
            raise EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Error(
                "unsupported learning-signal integrity status"
            )

        return EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2(
            eligibility_id=eligibility_id,
            integrity_id=integrity.integrity_id,
            signal_id=integrity.signal_id,
            evaluation_id=integrity.evaluation_id,
            feedback_id=integrity.feedback_id,
            outcome_id=integrity.outcome_id,
            execution_id=integrity.execution_id,
            preparation_id=integrity.preparation_id,
            decision_id=integrity.decision_id,
            proposal_id=integrity.proposal_id,
            assessment_id=integrity.assessment_id,
            environment_id=integrity.environment_id,
            expected_model_id=integrity.expected_model_id,
            observed_model_id=integrity.observed_model_id,
            signal_integrity_status=integrity.status,
            signal_status=integrity.signal_status,
            confidence=integrity.confidence,
            signal_fingerprint=integrity.signal_fingerprint,
            eligibility_status=eligibility_status,
            reasons=reasons or {"status": default_reason},
            lineage=lineage or {
                "eligibility_id": eligibility_id,
                "integrity_id": integrity.integrity_id,
                "signal_id": integrity.signal_id,
                "evaluation_id": integrity.evaluation_id,
                "feedback_id": integrity.feedback_id,
                "outcome_id": integrity.outcome_id,
                "execution_id": integrity.execution_id,
                "preparation_id": integrity.preparation_id,
                "decision_id": integrity.decision_id,
                "proposal_id": integrity.proposal_id,
                "assessment_id": integrity.assessment_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Error",
    "EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status",
    "EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2",
    "EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Service",
]
