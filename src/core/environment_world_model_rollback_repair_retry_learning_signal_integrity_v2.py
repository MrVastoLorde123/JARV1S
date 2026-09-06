"""M23.59: integrity validation of v2 rollback-repair retry learning signals."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_feedback_evaluation_v2 import (
    EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_learning_signal_v2 import (
    EnvironmentWorldModelRollbackRepairRetryLearningSignalV2,
    EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Status,
)


class EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2Error(RuntimeError):
    """Raised when learning-signal integrity evidence cannot be formed safely."""


class EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2Status(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"


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


def _canonical(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {str(key): _canonical(value[key]) for key in sorted(value, key=lambda item: str(item))}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    if isinstance(value, set):
        return sorted(
            (_canonical(item) for item in value),
            key=lambda item: json.dumps(item, sort_keys=True, separators=(",", ":")),
        )
    return value


def _signal_fingerprint(signal: EnvironmentWorldModelRollbackRepairRetryLearningSignalV2) -> str:
    payload = {
        "signal_id": signal.signal_id,
        "evaluation_id": signal.evaluation_id,
        "feedback_id": signal.feedback_id,
        "outcome_id": signal.outcome_id,
        "integrity_id": signal.integrity_id,
        "execution_id": signal.execution_id,
        "preparation_id": signal.preparation_id,
        "decision_id": signal.decision_id,
        "integrity_decision_id": signal.integrity_decision_id,
        "proposal_id": signal.proposal_id,
        "assessment_id": signal.assessment_id,
        "environment_id": signal.environment_id,
        "expected_model_id": signal.expected_model_id,
        "observed_model_id": signal.observed_model_id,
        "evaluation_status": signal.evaluation_status,
        "signal_status": signal.signal_status,
        "confidence": signal.confidence,
        "result_fingerprint": signal.result_fingerprint,
        "failure_reason": signal.failure_reason,
        "worker_id": signal.worker_id,
        "reasons": signal.reasons,
        "lineage": signal.lineage,
    }
    canonical = json.dumps(_canonical(payload), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2:
    """Immutable integrity evidence over one v2 learning signal."""

    integrity_id: str
    signal_id: str
    evaluation_id: str
    feedback_id: str
    outcome_id: str
    source_integrity_id: str
    execution_id: str
    preparation_id: str
    decision_id: str
    proposal_id: str
    assessment_id: str | None
    environment_id: str
    expected_model_id: str
    observed_model_id: str
    evaluation_status: EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Status
    signal_status: EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Status
    confidence: float
    signal_fingerprint: str
    status: EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2Status
    integrity_evaluation_id: str | None = None
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "integrity_id", "signal_id", "evaluation_id", "feedback_id", "outcome_id",
            "source_integrity_id", "execution_id", "preparation_id", "decision_id",
            "proposal_id", "environment_id", "expected_model_id", "observed_model_id",
            "signal_fingerprint",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        for name in ("assessment_id", "integrity_evaluation_id"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{name} must be None or a non-empty string")
        if not isinstance(self.evaluation_status, EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Status):
            raise TypeError("evaluation_status must be a feedback-evaluation v2 status")
        if not isinstance(self.signal_status, EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Status):
            raise TypeError("signal_status must be a learning-signal v2 status")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)):
            raise ValueError("confidence must be numeric")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if not isinstance(self.status, EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2Status):
            raise TypeError("status must be a learning-signal integrity v2 status")
        if self.status == EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2Status.VALID:
            if len(self.signal_fingerprint) != 64:
                raise ValueError("VALID integrity requires a SHA-256 signal fingerprint")
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
    def grants_authority(self) -> bool:
        return False

    @property
    def requests_retry(self) -> bool:
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


class EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2Service:
    """Verify one exact learning signal and emit inert integrity evidence."""

    def verify(
        self,
        signal: EnvironmentWorldModelRollbackRepairRetryLearningSignalV2,
        *,
        integrity_id: str,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2:
        if type(signal) is not EnvironmentWorldModelRollbackRepairRetryLearningSignalV2:
            raise TypeError("signal must be EnvironmentWorldModelRollbackRepairRetryLearningSignalV2")
        if not isinstance(integrity_id, str) or not integrity_id.strip():
            raise ValueError("integrity_id must be a non-empty string")
        fingerprint = _signal_fingerprint(signal)
        return EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2(
            integrity_id=integrity_id,
            signal_id=signal.signal_id,
            evaluation_id=signal.evaluation_id,
            feedback_id=signal.feedback_id,
            outcome_id=signal.outcome_id,
            source_integrity_id=signal.integrity_id,
            execution_id=signal.execution_id,
            preparation_id=signal.preparation_id,
            decision_id=signal.decision_id,
            proposal_id=signal.proposal_id,
            assessment_id=signal.assessment_id,
            environment_id=signal.environment_id,
            expected_model_id=signal.expected_model_id,
            observed_model_id=signal.observed_model_id,
            evaluation_status=signal.evaluation_status,
            signal_status=signal.signal_status,
            confidence=signal.confidence,
            signal_fingerprint=fingerprint,
            status=EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2Status.VALID,
            integrity_evaluation_id=signal.evaluation_id,
            reasons=reasons or {"status": "learning signal structurally validated and fingerprinted"},
            lineage=lineage or {
                "signal_id": signal.signal_id,
                "evaluation_id": signal.evaluation_id,
                "feedback_id": signal.feedback_id,
                "outcome_id": signal.outcome_id,
                "integrity_id": signal.integrity_id,
                "execution_id": signal.execution_id,
                "preparation_id": signal.preparation_id,
                "decision_id": signal.decision_id,
                "proposal_id": signal.proposal_id,
                "assessment_id": signal.assessment_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2Error",
    "EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2Status",
    "EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2",
    "EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2Service",
]
