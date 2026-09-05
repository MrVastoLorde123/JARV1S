"""Result-integrity boundary after future adaptation execution.

This module interprets an M22.42 execution result against the exact request
that produced it. The normalized outcome is immutable, identity-bound
evidence; it is not adaptation truth, authorization, retry, revocation, or
memory mutation.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping

from .learning_write_adaptation_evaluation_execution_feedback_execution import (
    LearningWriteAdaptationEvaluationExecutionRequest,
    LearningWriteAdaptationEvaluationExecutionResult,
    LearningWriteAdaptationEvaluationExecutionStatus,
)


class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityError(ValueError):
    """Raised when the M22.43 result-integrity contract is invalid."""


class LearningWriteAdaptationEvaluationExecutionFeedbackOutcomeStatus(str, Enum):
    """Normalized outcome status for one exact M22.42 execution."""

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
class LearningWriteAdaptationEvaluationExecutionFeedbackOutcome:
    """Immutable result-integrity evidence bound to one exact M22.42 execution."""

    execution_id: str
    preparation_id: str
    admission_id: str
    proposal_id: str
    decision_id: str
    evaluation_id: str
    decision_source_evaluation_id: str
    feedback_id: str
    source_feedback_id: str
    candidate_id: str
    source_candidate_id: str
    source_execution_id: str
    source_admission_id: str
    proposal_source_id: str
    domain: str
    source_policy_id: str
    policy_id: str
    status: LearningWriteAdaptationEvaluationExecutionFeedbackOutcomeStatus
    execution_result: Any = None
    result_fingerprint: str | None = None
    reason: str | None = None

    def __post_init__(self) -> None:
        for field_name, value in (
            ("execution_id", self.execution_id), ("preparation_id", self.preparation_id),
            ("admission_id", self.admission_id), ("proposal_id", self.proposal_id),
            ("decision_id", self.decision_id), ("evaluation_id", self.evaluation_id),
            ("decision_source_evaluation_id", self.decision_source_evaluation_id),
            ("feedback_id", self.feedback_id), ("source_feedback_id", self.source_feedback_id),
            ("candidate_id", self.candidate_id), ("source_candidate_id", self.source_candidate_id),
            ("source_execution_id", self.source_execution_id), ("source_admission_id", self.source_admission_id),
            ("proposal_source_id", self.proposal_source_id), ("domain", self.domain),
            ("source_policy_id", self.source_policy_id), ("policy_id", self.policy_id),
        ):
            if not isinstance(value, str) or not value.strip():
                raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityError(
                    f"{field_name} must be a non-empty string"
                )
        if not isinstance(self.status, LearningWriteAdaptationEvaluationExecutionFeedbackOutcomeStatus):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityError(
                "status must be a LearningWriteAdaptationEvaluationExecutionFeedbackOutcomeStatus member"
            )
        if self.status is LearningWriteAdaptationEvaluationExecutionFeedbackOutcomeStatus.SUCCEEDED:
            if not isinstance(self.result_fingerprint, str) or not self.result_fingerprint.strip():
                raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityError(
                    "a successful outcome requires a result fingerprint"
                )
            if self.reason is not None:
                raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityError(
                    "a successful outcome cannot contain a failure reason"
                )
        else:
            if not isinstance(self.reason, str) or not self.reason.strip():
                raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityError(
                    "a failed outcome requires a non-empty reason"
                )
            if self.result_fingerprint is not None:
                raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityError(
                    "a failed outcome cannot contain a result fingerprint"
                )
        object.__setattr__(self, "execution_result", _freeze(self.execution_result))

    def to_context(self) -> dict[str, object]:
        return {
            "learning_write_adaptation_evaluation_execution_feedback_outcome_id": self.execution_id,
            "learning_write_adaptation_evaluation_execution_id": self.execution_id,
            "learning_write_adaptation_evaluation_execution_preparation_id": self.preparation_id,
            "learning_write_adaptation_evaluation_execution_feedback_proposal_admission_id": self.admission_id,
            "learning_write_adaptation_evaluation_execution_feedback_proposal_id": self.proposal_id,
            "learning_write_adaptation_evaluation_execution_feedback_decision_id": self.decision_id,
            "learning_write_adaptation_evaluation_execution_feedback_evaluation_id": self.evaluation_id,
            "learning_write_adaptation_feedback_evaluation_id": self.decision_source_evaluation_id,
            "learning_write_adaptation_evaluation_execution_feedback_id": self.feedback_id,
            "learning_write_adaptation_source_feedback_id": self.source_feedback_id,
            "learning_write_adaptation_candidate_id": self.candidate_id,
            "learning_candidate_id": self.source_candidate_id,
            "learning_write_adaptation_source_execution_id": self.source_execution_id,
            "learning_write_adaptation_evaluation_execution_source_admission_id": self.source_admission_id,
            "learning_write_adaptation_evaluation_proposal_id": self.proposal_source_id,
            "learning_write_adaptation_domain": self.domain,
            "learning_write_adaptation_source_policy_id": self.source_policy_id,
            "learning_write_adaptation_evaluation_execution_policy_id": self.policy_id,
            "learning_write_adaptation_evaluation_execution_feedback_outcome_status": self.status.value,
            "execution_result_integrity_verified": True,
            "result_fingerprint": self.result_fingerprint,
            "execution_result": self.execution_result,
            "reason": self.reason,
            "adaptation_truth_proven": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
            "memory_mutation_allowed": False,
        }


class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityService:
    """Normalize exactly one M22.42 result against its exact execution request."""

    def interpret(
        self,
        result: LearningWriteAdaptationEvaluationExecutionResult,
        request: LearningWriteAdaptationEvaluationExecutionRequest,
    ) -> LearningWriteAdaptationEvaluationExecutionFeedbackOutcome:
        if not isinstance(result, LearningWriteAdaptationEvaluationExecutionResult):
            raise TypeError("result must be a LearningWriteAdaptationEvaluationExecutionResult")
        if not isinstance(request, LearningWriteAdaptationEvaluationExecutionRequest):
            raise TypeError("request must be a LearningWriteAdaptationEvaluationExecutionRequest")

        checks = (
            ("execution", result.execution_id, request.execution_id),
            ("preparation", result.preparation_id, request.preparation_id),
            ("admission", result.admission_id, request.admission_id),
            ("proposal", result.proposal_id, request.proposal_id),
            ("decision", result.decision_id, request.decision_id),
            ("evaluation", result.evaluation_id, request.evaluation_id),
            ("feedback", result.feedback_id, request.feedback_id),
            ("source feedback", result.source_feedback_id, request.source_feedback_id),
            ("candidate", result.candidate_id, request.candidate_id),
            ("source candidate", result.source_candidate_id, request.source_candidate_id),
            ("source execution", result.source_execution_id, request.source_execution_id),
            ("domain", result.domain, request.domain),
            ("policy", result.policy_id, request.policy_id),
        )
        for label, actual, expected in checks:
            if actual != expected:
                raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityError(
                    f"future adaptation execution feedback result {label} identity mismatch"
                )

        # M22.42 execution request carries the exact execution lineage available
        # at execution time. The richer source-admission/source-proposal/source-policy
        # lineage remains preserved downstream by the preparation artifact itself.
        if result.status is LearningWriteAdaptationEvaluationExecutionStatus.COMPLETED:
            fingerprint = self._fingerprint(result.execution_result)
            return self._build_success(request, result.execution_result, fingerprint)

        return self._build_failure(request, result.reason)

    @staticmethod
    def _build_success(
        request: LearningWriteAdaptationEvaluationExecutionRequest,
        execution_result: Any,
        fingerprint: str,
    ) -> LearningWriteAdaptationEvaluationExecutionFeedbackOutcome:
        return LearningWriteAdaptationEvaluationExecutionFeedbackOutcome(
            execution_id=request.execution_id,
            preparation_id=request.preparation_id,
            admission_id=request.admission_id,
            proposal_id=request.proposal_id,
            decision_id=request.decision_id,
            evaluation_id=request.evaluation_id,
            decision_source_evaluation_id=request.evaluation_id,
            feedback_id=request.feedback_id,
            source_feedback_id=request.source_feedback_id,
            candidate_id=request.candidate_id,
            source_candidate_id=request.source_candidate_id,
            source_execution_id=request.source_execution_id,
            source_admission_id=request.admission_id,
            proposal_source_id=request.proposal_id,
            domain=request.domain,
            source_policy_id=request.policy_id,
            policy_id=request.policy_id,
            status=LearningWriteAdaptationEvaluationExecutionFeedbackOutcomeStatus.SUCCEEDED,
            execution_result=execution_result,
            result_fingerprint=fingerprint,
        )

    @staticmethod
    def _build_failure(
        request: LearningWriteAdaptationEvaluationExecutionRequest,
        reason: str | None,
    ) -> LearningWriteAdaptationEvaluationExecutionFeedbackOutcome:
        return LearningWriteAdaptationEvaluationExecutionFeedbackOutcome(
            execution_id=request.execution_id,
            preparation_id=request.preparation_id,
            admission_id=request.admission_id,
            proposal_id=request.proposal_id,
            decision_id=request.decision_id,
            evaluation_id=request.evaluation_id,
            decision_source_evaluation_id=request.evaluation_id,
            feedback_id=request.feedback_id,
            source_feedback_id=request.source_feedback_id,
            candidate_id=request.candidate_id,
            source_candidate_id=request.source_candidate_id,
            source_execution_id=request.source_execution_id,
            source_admission_id=request.admission_id,
            proposal_source_id=request.proposal_id,
            domain=request.domain,
            source_policy_id=request.policy_id,
            policy_id=request.policy_id,
            status=LearningWriteAdaptationEvaluationExecutionFeedbackOutcomeStatus.FAILED,
            reason=reason,
        )

    @staticmethod
    def _fingerprint(value: Any) -> str:
        serialized = json.dumps(
            value,
            sort_keys=True,
            default=repr,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(serialized).hexdigest()
