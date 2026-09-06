"""M23.68: observational feedback from verified adaptation execution outcome."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_outcome_classification_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status,
)


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Error(RuntimeError):
    """Raised when adaptation execution feedback cannot be formed safely."""


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status(str, Enum):
    SUCCESS_SIGNAL = "SUCCESS_SIGNAL"
    FAILURE_SIGNAL = "FAILURE_SIGNAL"
    REJECTION_SIGNAL = "REJECTION_SIGNAL"


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
class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2:
    """Immutable observational feedback derived from one M23.67 classification."""

    feedback_id: str
    classification_id: str
    integrity_id: str
    execution_id: str
    handoff_id: str
    authorization_id: str
    validation_id: str
    proposal_id: str
    eligibility_id: str
    signal_id: str
    evaluation_id: str
    outcome_id: str
    preparation_id: str
    decision_id: str
    source_proposal_id: str
    source_integrity_id: str
    assessment_id: str | None
    environment_id: str
    expected_model_id: str
    observed_model_id: str
    execution_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status
    feedback_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status
    confidence: float
    signal_fingerprint: str
    proposal_fingerprint: str
    handoff_fingerprint: str
    result_fingerprint: str
    authority_principal_id: str | None
    executor_id: str | None
    failure_reason: str | None
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "feedback_id", "classification_id", "integrity_id", "execution_id", "handoff_id", "authorization_id",
            "validation_id", "proposal_id", "eligibility_id", "signal_id", "evaluation_id", "outcome_id",
            "preparation_id", "decision_id", "source_proposal_id", "source_integrity_id", "environment_id",
            "expected_model_id", "observed_model_id", "signal_fingerprint", "proposal_fingerprint",
            "handoff_fingerprint", "result_fingerprint",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.assessment_id is not None and (not isinstance(self.assessment_id, str) or not self.assessment_id.strip()):
            raise ValueError("assessment_id must be None or a non-empty string")
        if not isinstance(self.execution_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status):
            raise TypeError("execution_status must be an outcome-classification v2 status")
        if not isinstance(self.feedback_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status):
            raise TypeError("feedback_status must be an adaptation-execution feedback v2 status")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if self.authority_principal_id is not None and (not isinstance(self.authority_principal_id, str) or not self.authority_principal_id.strip()):
            raise ValueError("authority_principal_id must be None or a non-empty string")
        if self.executor_id is not None and (not isinstance(self.executor_id, str) or not self.executor_id.strip()):
            raise ValueError("executor_id must be None or a non-empty string")
        if self.failure_reason is not None and (not isinstance(self.failure_reason, str) or not self.failure_reason.strip()):
            raise ValueError("failure_reason must be None or a non-empty string")
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")

        expected = {
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status.SUCCESS:
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.SUCCESS_SIGNAL,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status.FAILURE:
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.FAILURE_SIGNAL,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status.REJECTED:
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.REJECTION_SIGNAL,
        }[self.execution_status]
        if self.feedback_status != expected:
            raise ValueError("feedback status does not match classified execution outcome")

        if self.feedback_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.SUCCESS_SIGNAL:
            if len(self.result_fingerprint) != 64 or self.result_fingerprint == "0" * 64 or self.failure_reason is not None:
                raise ValueError("SUCCESS_SIGNAL requires successful result evidence")
        elif self.feedback_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.FAILURE_SIGNAL:
            if self.failure_reason is None or self.result_fingerprint != "0" * 64:
                raise ValueError("FAILURE_SIGNAL requires failure evidence and zero result fingerprint")
        else:
            if self.authority_principal_id is not None or self.executor_id is not None:
                raise ValueError("REJECTION_SIGNAL cannot carry authority or executor evidence")
            if self.result_fingerprint != "0" * 64 or self.handoff_fingerprint != "0" * 64:
                raise ValueError("REJECTION_SIGNAL requires zero action fingerprints")
            if self.failure_reason is None:
                raise ValueError("REJECTION_SIGNAL requires rejection reason")

        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_advisory_only(self) -> bool:
        return True

    @property
    def creates_learning_signal(self) -> bool:
        return False

    @property
    def authorizes_retry(self) -> bool:
        return False

    @property
    def grants_authority(self) -> bool:
        return False

    @property
    def schedules_work(self) -> bool:
        return False

    @property
    def mutates_persistence(self) -> bool:
        return False

    @property
    def mutates_policy(self) -> bool:
        return False

    @property
    def mutates_memory(self) -> bool:
        return False


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Service:
    """Convert one verified outcome classification into inert feedback evidence."""

    def record(
        self,
        classification: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2,
        *,
        feedback_id: str,
        confidence: float = 1.0,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2:
        if type(classification) is not EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2:
            raise TypeError("classification must be EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2")
        if not isinstance(feedback_id, str) or not feedback_id.strip():
            raise ValueError("feedback_id must be a non-empty string")
        if isinstance(confidence, bool) or not isinstance(confidence, (int, float)) or not 0.0 <= float(confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")

        feedback_status = {
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status.SUCCESS:
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.SUCCESS_SIGNAL,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status.FAILURE:
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.FAILURE_SIGNAL,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status.REJECTED:
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.REJECTION_SIGNAL,
        }.get(classification.classification_status)
        if feedback_status is None:
            raise EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Error("unsupported classification status")

        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2(
            feedback_id=feedback_id,
            classification_id=classification.classification_id,
            integrity_id=classification.integrity_id,
            execution_id=classification.execution_id,
            handoff_id=classification.handoff_id,
            authorization_id=classification.authorization_id,
            validation_id=classification.validation_id,
            proposal_id=classification.proposal_id,
            eligibility_id=classification.eligibility_id,
            signal_id=classification.signal_id,
            evaluation_id=classification.evaluation_id,
            outcome_id=classification.outcome_id,
            preparation_id=classification.preparation_id,
            decision_id=classification.decision_id,
            source_proposal_id=classification.source_proposal_id,
            source_integrity_id=classification.source_integrity_id,
            assessment_id=classification.assessment_id,
            environment_id=classification.environment_id,
            expected_model_id=classification.expected_model_id,
            observed_model_id=classification.observed_model_id,
            execution_status=classification.classification_status,
            feedback_status=feedback_status,
            confidence=float(confidence),
            signal_fingerprint=classification.signal_fingerprint,
            proposal_fingerprint=classification.proposal_fingerprint,
            handoff_fingerprint=classification.handoff_fingerprint,
            result_fingerprint=classification.result_fingerprint,
            authority_principal_id=classification.authority_principal_id,
            executor_id=classification.executor_id,
            failure_reason=classification.failure_reason,
            reasons=reasons or {"status": f"{feedback_status.value.lower()} recorded as observational feedback"},
            lineage=lineage or {"classification_id": classification.classification_id, "integrity_id": classification.integrity_id, "execution_id": classification.execution_id},
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Error",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Service",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status",
]
