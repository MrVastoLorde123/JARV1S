"""M23.91: integrity validation of the M23.90 application learning signal v4."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_signal_v4 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningSignalV4,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningSignalV4Status,
)


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningSignalIntegrityV4Error(RuntimeError):
    """Raised when v4 application-learning-signal integrity evidence cannot be formed safely."""


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningSignalIntegrityV4Status(str, Enum):
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


def _learning_signal_fingerprint(
    signal: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningSignalV4,
) -> str:
    payload = {
        "signal_id": signal.signal_id,
        "evaluation_id": signal.evaluation_id,
        "feedback_id": signal.feedback_id,
        "feedback_source_id": signal.feedback_source_id,
        "classification_id": signal.classification_id,
        "integrity_id": signal.integrity_id,
        "application_id": signal.application_id,
        "decision_id": signal.decision_id,
        "proposal_id": signal.proposal_id,
        "outcome_id": signal.outcome_id,
        "outcome_status": signal.outcome_status,
        "feedback_status": signal.feedback_status,
        "confidence": signal.confidence,
        "signal_fingerprint": signal.signal_fingerprint,
        "result_fingerprint": signal.result_fingerprint,
        "application_fingerprint": signal.application_fingerprint,
        "failure_reason": signal.failure_reason,
        "evaluation_status": signal.evaluation_status,
        "signal_status": signal.signal_status,
        "reasons": signal.reasons,
        "lineage": signal.lineage,
    }
    canonical = json.dumps(
        _canonical(payload), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningSignalIntegrityV4:
    """Immutable integrity evidence over one exact M23.90 application learning signal v4."""

    integrity_id: str
    signal_id: str
    evaluation_id: str
    feedback_id: str
    feedback_source_id: str
    classification_id: str
    source_integrity_id: str
    application_id: str
    decision_id: str
    proposal_id: str
    outcome_id: str
    outcome_status: Any
    feedback_status: Any
    confidence: float
    signal_fingerprint: str
    result_fingerprint: str
    application_fingerprint: str
    failure_reason: str | None
    evaluation_status: Any
    signal_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningSignalV4Status
    status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningSignalIntegrityV4Status
    source_signal_fingerprint: str
    reasons: Mapping[str, Any] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "integrity_id", "signal_id", "evaluation_id", "feedback_id", "feedback_source_id", "classification_id",
            "source_integrity_id", "application_id", "decision_id", "proposal_id", "outcome_id",
            "signal_fingerprint", "result_fingerprint", "application_fingerprint", "source_signal_fingerprint",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)):
            raise ValueError("confidence must be numeric")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if self.failure_reason is not None and (not isinstance(self.failure_reason, str) or not self.failure_reason.strip()):
            raise ValueError("failure_reason must be None or a non-empty string")
        if not isinstance(
            self.signal_status,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningSignalV4Status,
        ):
            raise TypeError("signal_status has invalid enum type")
        if not isinstance(
            self.status,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningSignalIntegrityV4Status,
        ):
            raise TypeError("status has invalid enum type")
        if self.status is EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningSignalIntegrityV4Status.VALID:
            for name in ("signal_fingerprint", "source_signal_fingerprint"):
                if len(getattr(self, name)) != 64:
                    raise ValueError("VALID integrity requires SHA-256 fingerprints")
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_advisory_only(self) -> bool:
        return True

    @property
    def is_observational(self) -> bool:
        return True

    @property
    def grants_authority(self) -> bool:
        return False

    @property
    def authorizes_retry(self) -> bool:
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

    @property
    def schedules_work(self) -> bool:
        return False

    @property
    def executes(self) -> bool:
        return False


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningSignalIntegrityV4Service:
    """Verify one exact v4 application learning signal and emit inert integrity evidence."""

    def verify(
        self,
        signal: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningSignalV4,
        *,
        integrity_id: str,
        reasons: Mapping[str, Any] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningSignalIntegrityV4:
        if type(signal) is not EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningSignalV4:
            raise TypeError("signal must be an application learning signal v4 artifact")
        if not isinstance(integrity_id, str) or not integrity_id.strip():
            raise ValueError("integrity_id must be a non-empty string")
        fingerprint = _learning_signal_fingerprint(signal)
        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningSignalIntegrityV4(
            integrity_id=integrity_id,
            signal_id=signal.signal_id,
            evaluation_id=signal.evaluation_id,
            feedback_id=signal.feedback_id,
            feedback_source_id=signal.feedback_source_id,
            classification_id=signal.classification_id,
            source_integrity_id=signal.integrity_id,
            application_id=signal.application_id,
            decision_id=signal.decision_id,
            proposal_id=signal.proposal_id,
            outcome_id=signal.outcome_id,
            outcome_status=signal.outcome_status,
            feedback_status=signal.feedback_status,
            confidence=signal.confidence,
            signal_fingerprint=fingerprint,
            result_fingerprint=signal.result_fingerprint,
            application_fingerprint=signal.application_fingerprint,
            failure_reason=signal.failure_reason,
            evaluation_status=signal.evaluation_status,
            signal_status=signal.signal_status,
            status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningSignalIntegrityV4Status.VALID,
            source_signal_fingerprint=signal.signal_fingerprint,
            reasons=reasons if reasons is not None else {"status": "application learning signal v4 structurally validated and fingerprinted"},
            lineage=lineage if lineage is not None else {
                "integrity_id": integrity_id,
                "signal_id": signal.signal_id,
                "evaluation_id": signal.evaluation_id,
                "feedback_id": signal.feedback_id,
                "feedback_source_id": signal.feedback_source_id,
                "classification_id": signal.classification_id,
                "application_id": signal.application_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningSignalIntegrityV4Error",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningSignalIntegrityV4Status",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningSignalIntegrityV4",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningSignalIntegrityV4Service",
]
