"""Result-integrity boundary after future adaptation execution.

This module interprets an M22.34 execution result against the exact request
that produced it. The normalized outcome is immutable, identity-bound
evidence; it is not adaptation truth, authorization, retry, revocation, or
memory mutation.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from typing import Any

from .learning_write_adaptation_evaluation_execution import (
    LearningWriteAdaptationEvaluationExecutionRequest,
    LearningWriteAdaptationEvaluationExecutionResult,
    LearningWriteAdaptationEvaluationExecutionStatus,
)


class LearningWriteAdaptationEvaluationExecutionResultIntegrityError(ValueError):
    """Raised when the M22.34 execution-result integrity contract is invalid."""


class LearningWriteAdaptationEvaluationExecutionOutcomeStatus(str, Enum):
    """Normalized outcome status for one exact M22.34 execution."""

    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass(frozen=True)
class LearningWriteAdaptationEvaluationExecutionOutcome:
    """Immutable, identity-bound result observation for one M22.34 execution."""

    execution_id: str
    preparation_id: str
    admission_id: str
    proposal_id: str
    decision_id: str
    evaluation_id: str
    feedback_id: str
    source_feedback_id: str
    candidate_id: str
    source_candidate_id: str
    source_execution_id: str
    domain: str
    policy_id: str
    status: LearningWriteAdaptationEvaluationExecutionOutcomeStatus
    execution_result: Any = None
    result_fingerprint: str | None = None
    reason: str | None = None

    def __post_init__(self) -> None:
        for field_name, value in (
            ("execution_id", self.execution_id),
            ("preparation_id", self.preparation_id),
            ("admission_id", self.admission_id),
            ("proposal_id", self.proposal_id),
            ("decision_id", self.decision_id),
            ("evaluation_id", self.evaluation_id),
            ("feedback_id", self.feedback_id),
            ("source_feedback_id", self.source_feedback_id),
            ("candidate_id", self.candidate_id),
            ("source_candidate_id", self.source_candidate_id),
            ("source_execution_id", self.source_execution_id),
            ("domain", self.domain),
            ("policy_id", self.policy_id),
        ):
            if not isinstance(value, str) or not value.strip():
                raise LearningWriteAdaptationEvaluationExecutionResultIntegrityError(
                    f"{field_name} must be a non-empty string"
                )
        if not isinstance(self.status, LearningWriteAdaptationEvaluationExecutionOutcomeStatus):
            raise LearningWriteAdaptationEvaluationExecutionResultIntegrityError(
                "status must be a LearningWriteAdaptationEvaluationExecutionOutcomeStatus member"
            )
        if self.result_fingerprint is not None and (
            not isinstance(self.result_fingerprint, str) or not self.result_fingerprint.strip()
        ):
            raise LearningWriteAdaptationEvaluationExecutionResultIntegrityError(
                "result_fingerprint must be a non-empty string or None"
            )
        if self.reason is not None and not isinstance(self.reason, str):
            raise LearningWriteAdaptationEvaluationExecutionResultIntegrityError(
                "reason must be a string or None"
            )
        if self.status is LearningWriteAdaptationEvaluationExecutionOutcomeStatus.SUCCEEDED:
            if self.result_fingerprint is None:
                raise LearningWriteAdaptationEvaluationExecutionResultIntegrityError(
                    "a successful outcome requires a result fingerprint"
                )
            if self.reason is not None:
                raise LearningWriteAdaptationEvaluationExecutionResultIntegrityError(
                    "a successful outcome cannot contain a failure reason"
                )
        else:
            if self.reason is None or not self.reason.strip():
                raise LearningWriteAdaptationEvaluationExecutionResultIntegrityError(
                    "a failed outcome requires a reason"
                )
            if self.result_fingerprint is not None:
                raise LearningWriteAdaptationEvaluationExecutionResultIntegrityError(
                    "a failed outcome cannot contain a result fingerprint"
                )

    def to_context(self) -> dict[str, object]:
        return {
            "learning_write_adaptation_evaluation_execution_outcome_id": self.execution_id,
            "learning_write_adaptation_evaluation_execution_id": self.execution_id,
            "learning_write_adaptation_evaluation_execution_preparation_id": self.preparation_id,
            "learning_write_adaptation_evaluation_proposal_admission_id": self.admission_id,
            "learning_write_adaptation_evaluation_proposal_id": self.proposal_id,
            "learning_write_adaptation_evaluation_decision_id": self.decision_id,
            "learning_write_adaptation_feedback_evaluation_id": self.evaluation_id,
            "learning_write_adaptation_feedback_id": self.feedback_id,
            "learning_write_adaptation_source_feedback_id": self.source_feedback_id,
            "learning_write_adaptation_candidate_id": self.candidate_id,
            "learning_candidate_id": self.source_candidate_id,
            "learning_write_adaptation_source_execution_id": self.source_execution_id,
            "learning_write_adaptation_domain": self.domain,
            "learning_write_adaptation_evaluation_execution_policy_id": self.policy_id,
            "learning_write_adaptation_evaluation_execution_outcome_status": self.status.value,
            "execution_result_integrity_verified": True,
            "result_fingerprint": self.result_fingerprint,
            "reason": self.reason,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
            "memory_mutation_allowed": False,
            "adaptation_truth_proven": False,
        }


class LearningWriteAdaptationEvaluationExecutionResultIntegrityService:
    """Normalize exactly one M22.34 execution result against its exact request."""

    def interpret(
        self,
        result: LearningWriteAdaptationEvaluationExecutionResult,
        request: LearningWriteAdaptationEvaluationExecutionRequest,
    ) -> LearningWriteAdaptationEvaluationExecutionOutcome:
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
                raise LearningWriteAdaptationEvaluationExecutionResultIntegrityError(
                    f"adaptation evaluation execution {label} identity mismatch"
                )

        if result.status is LearningWriteAdaptationEvaluationExecutionStatus.COMPLETED:
            fingerprint = self._fingerprint(result.execution_result)
            return LearningWriteAdaptationEvaluationExecutionOutcome(
                execution_id=result.execution_id,
                preparation_id=result.preparation_id,
                admission_id=result.admission_id,
                proposal_id=result.proposal_id,
                decision_id=result.decision_id,
                evaluation_id=result.evaluation_id,
                feedback_id=result.feedback_id,
                source_feedback_id=result.source_feedback_id,
                candidate_id=result.candidate_id,
                source_candidate_id=result.source_candidate_id,
                source_execution_id=result.source_execution_id,
                domain=result.domain,
                policy_id=result.policy_id,
                status=LearningWriteAdaptationEvaluationExecutionOutcomeStatus.SUCCEEDED,
                execution_result=result.execution_result,
                result_fingerprint=fingerprint,
            )

        return LearningWriteAdaptationEvaluationExecutionOutcome(
            execution_id=result.execution_id,
            preparation_id=result.preparation_id,
            admission_id=result.admission_id,
            proposal_id=result.proposal_id,
            decision_id=result.decision_id,
            evaluation_id=result.evaluation_id,
            feedback_id=result.feedback_id,
            source_feedback_id=result.source_feedback_id,
            candidate_id=result.candidate_id,
            source_candidate_id=result.source_candidate_id,
            source_execution_id=result.source_execution_id,
            domain=result.domain,
            policy_id=result.policy_id,
            status=LearningWriteAdaptationEvaluationExecutionOutcomeStatus.FAILED,
            reason=result.reason,
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
