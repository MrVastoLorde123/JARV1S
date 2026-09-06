"""M23.81: integrity validation of v3 adaptation-application learning signals."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_signal_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalV3Status,
)


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalIntegrityV3Error(RuntimeError):
    """Raised when v3 application-learning-signal integrity evidence cannot be formed safely."""


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalIntegrityV3Status(str, Enum):
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
    signal: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalV3,
) -> str:
    payload = {
        "signal_id": signal.signal_id,
        "evaluation_id": signal.evaluation_id,
        "feedback_id": signal.feedback_id,
        "classification_id": signal.classification_id,
        "integrity_id": signal.integrity_id,
        "application_id": signal.application_id,
        "decision_id": signal.decision_id,
        "proposal_id": signal.proposal_id,
        "source_proposal_id": signal.source_proposal_id,
        "eligibility_id": signal.eligibility_id,
        "source_integrity_id": signal.source_integrity_id,
        "feedback_signal_id": signal.feedback_signal_id,
        "feedback_source_id": signal.feedback_source_id,
        "source_evaluation_id": signal.source_evaluation_id,
        "execution_id": signal.execution_id,
        "handoff_id": signal.handoff_id,
        "authorization_id": signal.authorization_id,
        "validation_id": signal.validation_id,
        "source_signal_id": signal.source_signal_id,
        "outcome_id": signal.outcome_id,
        "preparation_id": signal.preparation_id,
        "assessment_id": signal.assessment_id,
        "environment_id": signal.environment_id,
        "expected_model_id": signal.expected_model_id,
        "observed_model_id": signal.observed_model_id,
        "proposal_kind": signal.proposal_kind,
        "proposal_status": signal.proposal_status,
        "decision_status": signal.decision_status,
        "application_status": signal.application_status,
        "integrity_status": signal.integrity_status,
        "outcome_status": signal.outcome_status,
        "feedback_status": signal.feedback_status,
        "evaluation_status": signal.evaluation_status,
        "signal_status": signal.signal_status,
        "confidence": signal.confidence,
        "signal_fingerprint": signal.signal_fingerprint,
        "upstream_proposal_fingerprint": signal.upstream_proposal_fingerprint,
        "handoff_fingerprint": signal.handoff_fingerprint,
        "result_fingerprint": signal.result_fingerprint,
        "application_fingerprint": signal.application_fingerprint,
        "authority_principal_id": signal.authority_principal_id,
        "executor_id": signal.executor_id,
        "failure_reason": signal.failure_reason,
        "reasons": signal.reasons,
        "lineage": signal.lineage,
    }
    canonical = json.dumps(
        _canonical(payload), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalIntegrityV3:
    """Immutable integrity evidence over one v3 application learning signal."""

    integrity_id: str
    signal_id: str
    evaluation_id: str
    feedback_id: str
    classification_id: str
    source_integrity_id: str
    application_id: str
    decision_id: str
    proposal_id: str
    source_proposal_id: str
    eligibility_id: str
    feedback_signal_id: str
    feedback_source_id: str
    source_evaluation_id: str
    execution_id: str
    handoff_id: str
    authorization_id: str
    validation_id: str
    source_signal_id: str
    outcome_id: str
    preparation_id: str
    assessment_id: str | None
    environment_id: str
    expected_model_id: str
    observed_model_id: str
    proposal_kind: str
    proposal_status: Any
    decision_status: Any
    application_status: Any
    integrity_status: Any
    outcome_status: Any
    feedback_status: Any
    evaluation_status: Any
    signal_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalV3Status
    confidence: float
    signal_fingerprint: str
    upstream_proposal_fingerprint: str
    handoff_fingerprint: str
    result_fingerprint: str
    application_fingerprint: str
    authority_principal_id: str | None
    executor_id: str | None
    failure_reason: str | None
    status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalIntegrityV3Status
    integrity_evaluation_id: str | None = None
    reasons: Mapping[str, Any] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "integrity_id", "signal_id", "evaluation_id", "feedback_id", "classification_id", "source_integrity_id",
            "application_id", "decision_id", "proposal_id", "source_proposal_id", "eligibility_id", "feedback_signal_id",
            "feedback_source_id", "source_evaluation_id", "execution_id", "handoff_id", "authorization_id", "validation_id",
            "source_signal_id", "outcome_id", "preparation_id", "environment_id", "expected_model_id", "observed_model_id",
            "proposal_kind", "signal_fingerprint", "upstream_proposal_fingerprint", "handoff_fingerprint",
            "result_fingerprint", "application_fingerprint",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        for name in ("assessment_id", "authority_principal_id", "executor_id", "integrity_evaluation_id"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{name} must be None or a non-empty string")
        if not isinstance(
            self.signal_status,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalV3Status,
        ):
            raise TypeError("signal_status must be an application learning-signal v3 status")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)):
            raise ValueError("confidence must be numeric")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if not isinstance(
            self.status,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalIntegrityV3Status,
        ):
            raise TypeError("status must be an application learning-signal integrity v3 status")
        if self.status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalIntegrityV3Status.VALID:
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
    def is_observational(self) -> bool:
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

    @property
    def schedules_work(self) -> bool:
        return False

    @property
    def executes_action(self) -> bool:
        return False


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalIntegrityV3Service:
    """Verify one exact v3 application learning signal and emit inert integrity evidence."""

    def verify(
        self,
        signal: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalV3,
        *,
        integrity_id: str,
        reasons: Mapping[str, Any] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalIntegrityV3:
        if type(signal) is not EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalV3:
            raise TypeError(
                "signal must be EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalV3"
            )
        if not isinstance(integrity_id, str) or not integrity_id.strip():
            raise ValueError("integrity_id must be a non-empty string")
        fingerprint = _learning_signal_fingerprint(signal)
        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalIntegrityV3(
            integrity_id=integrity_id,
            signal_id=signal.signal_id,
            evaluation_id=signal.evaluation_id,
            feedback_id=signal.feedback_id,
            classification_id=signal.classification_id,
            source_integrity_id=signal.integrity_id,
            application_id=signal.application_id,
            decision_id=signal.decision_id,
            proposal_id=signal.proposal_id,
            source_proposal_id=signal.source_proposal_id,
            eligibility_id=signal.eligibility_id,
            feedback_signal_id=signal.feedback_signal_id,
            feedback_source_id=signal.feedback_source_id,
            source_evaluation_id=signal.source_evaluation_id,
            execution_id=signal.execution_id,
            handoff_id=signal.handoff_id,
            authorization_id=signal.authorization_id,
            validation_id=signal.validation_id,
            source_signal_id=signal.source_signal_id,
            outcome_id=signal.outcome_id,
            preparation_id=signal.preparation_id,
            assessment_id=signal.assessment_id,
            environment_id=signal.environment_id,
            expected_model_id=signal.expected_model_id,
            observed_model_id=signal.observed_model_id,
            proposal_kind=signal.proposal_kind,
            proposal_status=signal.proposal_status,
            decision_status=signal.decision_status,
            application_status=signal.application_status,
            integrity_status=signal.integrity_status,
            outcome_status=signal.outcome_status,
            feedback_status=signal.feedback_status,
            evaluation_status=signal.evaluation_status,
            signal_status=signal.signal_status,
            confidence=signal.confidence,
            signal_fingerprint=fingerprint,
            upstream_proposal_fingerprint=signal.upstream_proposal_fingerprint,
            handoff_fingerprint=signal.handoff_fingerprint,
            result_fingerprint=signal.result_fingerprint,
            application_fingerprint=signal.application_fingerprint,
            authority_principal_id=signal.authority_principal_id,
            executor_id=signal.executor_id,
            failure_reason=signal.failure_reason,
            status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalIntegrityV3Status.VALID,
            integrity_evaluation_id=signal.evaluation_id,
            reasons=reasons if reasons is not None else {"status": "application learning signal v3 structurally validated and fingerprinted"},
            lineage=lineage if lineage is not None else {
                "signal_id": signal.signal_id,
                "evaluation_id": signal.evaluation_id,
                "feedback_id": signal.feedback_id,
                "classification_id": signal.classification_id,
                "integrity_id": signal.integrity_id,
                "application_id": signal.application_id,
                "decision_id": signal.decision_id,
                "proposal_id": signal.proposal_id,
                "feedback_signal_id": signal.feedback_signal_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalIntegrityV3Error",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalIntegrityV3Status",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalIntegrityV3",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalIntegrityV3Service",
]
