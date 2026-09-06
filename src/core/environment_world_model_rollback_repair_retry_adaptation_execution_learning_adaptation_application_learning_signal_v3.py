"""M23.80: advisory learning signal derived from v3 application feedback evaluation."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_feedback_evaluation_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_integrity_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_outcome_classification_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationOutcomeClassificationV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_decision_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status,
)


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalV3Error(RuntimeError):
    pass


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalV3Status(str, Enum):
    POSITIVE_SIGNAL = "POSITIVE_SIGNAL"
    NEGATIVE_SIGNAL = "NEGATIVE_SIGNAL"
    REJECTION_SIGNAL = "REJECTION_SIGNAL"


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(k): _freeze(v) for k, v in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(v) for v in value)
    if isinstance(value, tuple):
        return tuple(_freeze(v) for v in value)
    if isinstance(value, set):
        return frozenset(_freeze(v) for v in value)
    return value


@dataclass(frozen=True)
class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalV3:
    signal_id: str
    evaluation_id: str
    feedback_id: str
    classification_id: str
    integrity_id: str
    application_id: str
    decision_id: str
    proposal_id: str
    source_proposal_id: str
    eligibility_id: str
    source_integrity_id: str
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
    decision_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status
    application_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status
    integrity_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Status
    outcome_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationOutcomeClassificationV3Status
    feedback_status: Any
    evaluation_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Status
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
    reasons: Mapping[str, Any] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "signal_id", "evaluation_id", "feedback_id", "classification_id", "integrity_id", "application_id", "decision_id",
            "proposal_id", "source_proposal_id", "eligibility_id", "source_integrity_id", "feedback_signal_id", "feedback_source_id",
            "source_evaluation_id", "execution_id", "handoff_id", "authorization_id", "validation_id", "source_signal_id", "outcome_id",
            "preparation_id", "environment_id", "expected_model_id", "observed_model_id", "proposal_kind", "signal_fingerprint",
            "upstream_proposal_fingerprint", "handoff_fingerprint", "result_fingerprint", "application_fingerprint",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        for name in ("assessment_id", "authority_principal_id", "executor_id"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{name} must be None or a non-empty string")
        if self.failure_reason is not None and (not isinstance(self.failure_reason, str) or not self.failure_reason.strip()):
            raise ValueError("failure_reason must be None or a non-empty string")
        for name, enum_type in (
            ("decision_status", EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status),
            ("application_status", EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status),
            ("integrity_status", EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Status),
            ("outcome_status", EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationOutcomeClassificationV3Status),
            ("evaluation_status", EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Status),
            ("signal_status", EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalV3Status),
        ):
            if not isinstance(getattr(self, name), enum_type):
                raise TypeError(f"{name} has invalid enum type")
        if self.integrity_status != EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Status.VALID:
            raise ValueError("learning signal requires VALID application-integrity-backed evidence")
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")
        expected = {
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Status.SUCCESS_EVALUATION: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalV3Status.POSITIVE_SIGNAL,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Status.FAILURE_EVALUATION: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalV3Status.NEGATIVE_SIGNAL,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Status.REJECTION_EVALUATION: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalV3Status.REJECTION_SIGNAL,
        }[self.evaluation_status]
        if self.signal_status != expected:
            raise ValueError("signal status does not match evaluation status")
        if self.evaluation_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Status.REJECTION_EVALUATION:
            if self.failure_reason is not None or self.authority_principal_id is not None or self.executor_id is not None:
                raise ValueError("REJECTION_SIGNAL cannot carry failure, authority, or executor evidence")
            if self.result_fingerprint != "0" * 64 or self.handoff_fingerprint != "0" * 64:
                raise ValueError("REJECTION_SIGNAL requires zero action fingerprints")
        elif self.evaluation_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Status.FAILURE_EVALUATION:
            if self.failure_reason is None or self.result_fingerprint != "0" * 64:
                raise ValueError("NEGATIVE_SIGNAL requires failure evidence and zero result fingerprint")
        else:
            if self.failure_reason is not None:
                raise ValueError("POSITIVE_SIGNAL cannot carry failure evidence")

        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_advisory_only(self) -> bool: return True
    @property
    def is_observational(self) -> bool: return True
    @property
    def recommends_retry(self) -> bool: return False
    @property
    def requests_retry(self) -> bool: return False
    @property
    def grants_authority(self) -> bool: return False
    @property
    def updates_model(self) -> bool: return False
    @property
    def mutates_memory(self) -> bool: return False
    @property
    def mutates_policy(self) -> bool: return False
    @property
    def mutates_persistence(self) -> bool: return False
    @property
    def schedules_work(self) -> bool: return False
    @property
    def executes_action(self) -> bool: return False


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalV3Service:
    def emit(self, evaluation: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3, *, signal_id: str, reasons: Mapping[str, Any] | None = None, lineage: Mapping[str, Any] | None = None) -> EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalV3:
        if type(evaluation) is not EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3:
            raise TypeError("evaluation must be an adaptation-application feedback-evaluation v3 artifact")
        if not isinstance(signal_id, str) or not signal_id.strip():
            raise ValueError("signal_id must be a non-empty string")
        expected = {
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Status.SUCCESS_EVALUATION: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalV3Status.POSITIVE_SIGNAL,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Status.FAILURE_EVALUATION: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalV3Status.NEGATIVE_SIGNAL,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Status.REJECTION_EVALUATION: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalV3Status.REJECTION_SIGNAL,
        }
        signal_status = expected.get(evaluation.evaluation_status)
        if signal_status is None:
            raise EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalV3Error("unsupported evaluation status")
        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalV3(
            signal_id=signal_id,
            evaluation_id=evaluation.evaluation_id,
            feedback_id=evaluation.feedback_id,
            classification_id=evaluation.classification_id,
            integrity_id=evaluation.integrity_id,
            application_id=evaluation.application_id,
            decision_id=evaluation.decision_id,
            proposal_id=evaluation.proposal_id,
            source_proposal_id=evaluation.source_proposal_id,
            eligibility_id=evaluation.eligibility_id,
            source_integrity_id=evaluation.source_integrity_id,
            feedback_signal_id=evaluation.signal_id,
            feedback_source_id=evaluation.feedback_source_id,
            source_evaluation_id=evaluation.source_evaluation_id,
            execution_id=evaluation.execution_id,
            handoff_id=evaluation.handoff_id,
            authorization_id=evaluation.authorization_id,
            validation_id=evaluation.validation_id,
            source_signal_id=evaluation.source_signal_id,
            outcome_id=evaluation.outcome_id,
            preparation_id=evaluation.preparation_id,
            assessment_id=evaluation.assessment_id,
            environment_id=evaluation.environment_id,
            expected_model_id=evaluation.expected_model_id,
            observed_model_id=evaluation.observed_model_id,
            proposal_kind=evaluation.proposal_kind,
            proposal_status=evaluation.proposal_status,
            decision_status=evaluation.decision_status,
            application_status=evaluation.application_status,
            integrity_status=evaluation.integrity_status,
            outcome_status=evaluation.outcome_status,
            feedback_status=evaluation.feedback_status,
            evaluation_status=evaluation.evaluation_status,
            signal_status=signal_status,
            confidence=evaluation.confidence,
            signal_fingerprint=evaluation.signal_fingerprint,
            upstream_proposal_fingerprint=evaluation.upstream_proposal_fingerprint,
            handoff_fingerprint=evaluation.handoff_fingerprint,
            result_fingerprint=evaluation.result_fingerprint,
            application_fingerprint=evaluation.application_fingerprint,
            authority_principal_id=evaluation.authority_principal_id,
            executor_id=evaluation.executor_id,
            failure_reason=evaluation.failure_reason,
            reasons=reasons if reasons is not None else {"status": signal_status.value},
            lineage=lineage if lineage is not None else {"evaluation_id": evaluation.evaluation_id, "feedback_id": evaluation.feedback_id, "application_id": evaluation.application_id},
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalV3Error",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalV3Status",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalV3",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalV3Service",
]
