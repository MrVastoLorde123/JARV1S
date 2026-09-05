"""Result-integrity boundary after M22.50 execution attempt."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping

from .learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_decision_proposal_admission_preparation_execution import (
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionRequest,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResult,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionStatus,
)


class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityError(ValueError):
    """Raised when the M22.51 result-integrity contract is invalid."""


class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityStatus(str, Enum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze(item) for item in value)
    return value


@dataclass(frozen=True)
class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrity:
    integrity_id: str
    execution_id: str
    preparation_id: str
    admission_id: str
    proposal_id: str
    decision_id: str
    evaluation_id: str
    feedback_id: str
    outcome_id: str
    source_admission_id: str
    source_proposal_id: str
    decision_source_evaluation_id: str
    evaluation_id_from_feedback: str
    source_feedback_id: str
    candidate_id: str
    source_candidate_id: str
    execution_source_id: str
    source_execution_id: str
    domain: str
    source_policy_id: str
    policy_id: str
    status: LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityStatus
    execution_result: Any = None
    result_fingerprint: str | None = None
    reason: str | None = None

    def __post_init__(self) -> None:
        for name in (
            "integrity_id", "execution_id", "preparation_id", "admission_id", "proposal_id",
            "decision_id", "evaluation_id", "feedback_id", "outcome_id", "source_admission_id",
            "source_proposal_id", "decision_source_evaluation_id", "evaluation_id_from_feedback",
            "source_feedback_id", "candidate_id", "source_candidate_id", "execution_source_id",
            "source_execution_id", "domain", "source_policy_id", "policy_id",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityError(f"{name} must be a non-empty string")
        if not isinstance(self.status, LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityStatus):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityError("invalid integrity status")
        if self.status is LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityStatus.SUCCEEDED:
            if not isinstance(self.result_fingerprint, str) or not self.result_fingerprint.strip():
                raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityError("successful integrity outcome requires a fingerprint")
            if self.reason is not None:
                raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityError("successful integrity outcome cannot carry a failure reason")
        else:
            if not isinstance(self.reason, str) or not self.reason.strip():
                raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityError("failed integrity outcome requires a non-empty reason")
            if self.result_fingerprint is not None:
                raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityError("failed integrity outcome cannot carry a fingerprint")
        object.__setattr__(self, "execution_result", _freeze(self.execution_result))


class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityService:
    """Normalize one exact M22.50 execution request/result pair into integrity evidence."""

    def evaluate(self, execution_result, execution_request):
        if not isinstance(execution_result, LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResult):
            raise TypeError("execution_result must be a LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResult")
        if not isinstance(execution_request, LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionRequest):
            raise TypeError("execution_request must be a LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionRequest")
        for label, actual, expected in (
            ("execution", execution_result.execution_id, execution_request.execution_id),
            ("preparation", execution_result.preparation_id, execution_request.preparation_id),
            ("admission", execution_result.admission_id, execution_request.admission_id),
            ("proposal", execution_result.proposal_id, execution_request.proposal_id),
            ("decision", execution_result.decision_id, execution_request.decision_id),
            ("evaluation", execution_result.evaluation_id, execution_request.evaluation_id),
            ("feedback", execution_result.feedback_id, execution_request.feedback_id),
            ("outcome", execution_result.outcome_id, execution_request.outcome_id),
            ("source admission", execution_result.source_admission_id, execution_request.source_admission_id),
            ("source proposal", execution_result.source_proposal_id, execution_request.source_proposal_id),
            ("decision source evaluation", execution_result.decision_source_evaluation_id, execution_request.decision_source_evaluation_id),
            ("evaluation from feedback", execution_result.evaluation_id_from_feedback, execution_request.evaluation_id_from_feedback),
            ("source feedback", execution_result.source_feedback_id, execution_request.source_feedback_id),
            ("candidate", execution_result.candidate_id, execution_request.candidate_id),
            ("source candidate", execution_result.source_candidate_id, execution_request.source_candidate_id),
            ("execution source", execution_result.execution_source_id, execution_request.execution_source_id),
            ("source execution", execution_result.source_execution_id, execution_request.source_execution_id),
            ("domain", execution_result.domain, execution_request.domain),
            ("source policy", execution_result.source_policy_id, execution_request.source_policy_id),
            ("policy", execution_result.policy_id, execution_request.policy_id),
        ):
            if actual != expected:
                raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityError(f"execution result {label} identity does not match request")
        integrity_id = self._integrity_id(execution_result, execution_request)
        base = dict(
            integrity_id=integrity_id, execution_id=execution_result.execution_id,
            preparation_id=execution_result.preparation_id, admission_id=execution_result.admission_id,
            proposal_id=execution_result.proposal_id, decision_id=execution_result.decision_id,
            evaluation_id=execution_result.evaluation_id, feedback_id=execution_result.feedback_id,
            outcome_id=execution_result.outcome_id, source_admission_id=execution_result.source_admission_id,
            source_proposal_id=execution_result.source_proposal_id,
            decision_source_evaluation_id=execution_result.decision_source_evaluation_id,
            evaluation_id_from_feedback=execution_result.evaluation_id_from_feedback,
            source_feedback_id=execution_result.source_feedback_id, candidate_id=execution_result.candidate_id,
            source_candidate_id=execution_result.source_candidate_id, execution_source_id=execution_result.execution_source_id,
            source_execution_id=execution_result.source_execution_id, domain=execution_result.domain,
            source_policy_id=execution_result.source_policy_id, policy_id=execution_result.policy_id,
        )
        if execution_result.status is LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionStatus.COMPLETED:
            serialized = json.dumps(execution_result.execution_result, sort_keys=True, default=repr, separators=(",", ":")).encode("utf-8")
            return LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrity(
                **base, status=LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityStatus.SUCCEEDED,
                execution_result=execution_result.execution_result, result_fingerprint=hashlib.sha256(serialized).hexdigest()
            )
        if execution_result.reason is None or not execution_result.reason.strip():
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityError("failed execution result requires a non-empty reason")
        return LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrity(
            **base, status=LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResultIntegrityStatus.FAILED,
            reason=execution_result.reason
        )

    @staticmethod
    def _integrity_id(execution_result, execution_request) -> str:
        serialized = json.dumps({
            "execution_id": execution_result.execution_id, "preparation_id": execution_result.preparation_id,
            "status": execution_result.status.value, "result": execution_result.execution_result,
            "reason": execution_result.reason, "request_execution_id": execution_request.execution_id,
        }, sort_keys=True, default=repr, separators=(",", ":")).encode("utf-8")
        return "adaptation-evaluation-execution-feedback-result-integrity-preparation-execution-result-integrity-" + hashlib.sha256(serialized).hexdigest()[:24]
