"""Integrity boundary after learning-write adaptation execution.

This module interprets an adaptation execution result against the exact
execution request that produced it. The normalized outcome is immutable,
identity-bound evidence; it is not adaptation truth, authorization, retry,
revocation, or memory mutation.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from typing import Any, Mapping

from .learning_write_adaptation_execution import (
    LearningWriteAdaptationExecutionRequest,
    LearningWriteAdaptationExecutionResult,
    LearningWriteAdaptationExecutionStatus,
)


class LearningWriteAdaptationOutcomeError(ValueError):
    """Raised when the adaptation-outcome integrity contract is invalid."""


class LearningWriteAdaptationOutcomeStatus(str, Enum):
    """Normalized status of one adaptation execution outcome."""

    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass(frozen=True)
class LearningWriteAdaptationOutcome:
    """Immutable, identity-bound outcome observation for one adaptation execution."""

    execution_id: str
    admission_id: str
    proposal_id: str
    decision_id: str
    candidate_id: str
    feedback_id: str
    source_candidate_id: str
    domain: str
    status: LearningWriteAdaptationOutcomeStatus
    adaptation_result: Any = None
    result_fingerprint: str | None = None
    reason: str | None = None

    def __post_init__(self) -> None:
        for field_name, value in (
            ("execution_id", self.execution_id),
            ("admission_id", self.admission_id),
            ("proposal_id", self.proposal_id),
            ("decision_id", self.decision_id),
            ("candidate_id", self.candidate_id),
            ("feedback_id", self.feedback_id),
            ("source_candidate_id", self.source_candidate_id),
            ("domain", self.domain),
        ):
            if not isinstance(value, str) or not value.strip():
                raise LearningWriteAdaptationOutcomeError(
                    f"{field_name} must be a non-empty string"
                )
        if not isinstance(self.status, LearningWriteAdaptationOutcomeStatus):
            raise LearningWriteAdaptationOutcomeError(
                "status must be a LearningWriteAdaptationOutcomeStatus member"
            )
        if self.result_fingerprint is not None and (
            not isinstance(self.result_fingerprint, str) or not self.result_fingerprint.strip()
        ):
            raise LearningWriteAdaptationOutcomeError(
                "result_fingerprint must be a non-empty string or None"
            )
        if self.reason is not None and not isinstance(self.reason, str):
            raise LearningWriteAdaptationOutcomeError("reason must be a string or None")
        if self.status is LearningWriteAdaptationOutcomeStatus.SUCCEEDED:
            if self.result_fingerprint is None:
                raise LearningWriteAdaptationOutcomeError(
                    "a successful outcome requires a result fingerprint"
                )
            if self.reason is not None:
                raise LearningWriteAdaptationOutcomeError(
                    "a successful outcome cannot contain a failure reason"
                )
        else:
            if self.reason is None or not self.reason.strip():
                raise LearningWriteAdaptationOutcomeError(
                    "a failed outcome requires a reason"
                )
            if self.result_fingerprint is not None:
                raise LearningWriteAdaptationOutcomeError(
                    "a failed outcome cannot contain a result fingerprint"
                )

    def to_context(self) -> dict[str, object]:
        return {
            "learning_write_adaptation_outcome_execution_id": self.execution_id,
            "learning_write_adaptation_outcome_admission_id": self.admission_id,
            "learning_write_adaptation_outcome_proposal_id": self.proposal_id,
            "learning_write_adaptation_outcome_decision_id": self.decision_id,
            "learning_write_adaptation_outcome_candidate_id": self.candidate_id,
            "learning_write_feedback_id": self.feedback_id,
            "learning_candidate_id": self.source_candidate_id,
            "learning_write_adaptation_domain": self.domain,
            "learning_write_adaptation_outcome_status": self.status.value,
            "adaptation_applied": self.status is LearningWriteAdaptationOutcomeStatus.SUCCEEDED,
            "result_fingerprint": self.result_fingerprint,
            "reason": self.reason,
            "learning_written": False,
            "memory_mutated": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
        }


class LearningWriteAdaptationOutcomeService:
    """Normalize an adaptation execution result without granting authority."""

    def interpret(
        self,
        result: LearningWriteAdaptationExecutionResult,
        request: LearningWriteAdaptationExecutionRequest,
    ) -> LearningWriteAdaptationOutcome:
        if not isinstance(result, LearningWriteAdaptationExecutionResult):
            raise TypeError("result must be a LearningWriteAdaptationExecutionResult")
        if not isinstance(request, LearningWriteAdaptationExecutionRequest):
            raise TypeError("request must be a LearningWriteAdaptationExecutionRequest")

        checks = (
            ("execution", result.execution_id, request.execution_id),
            ("admission", result.admission_id, request.admission_id),
            ("proposal", result.proposal_id, request.proposal_id),
            ("decision", result.decision_id, request.decision_id),
            ("candidate", result.candidate_id, request.candidate_id),
            ("feedback", result.feedback_id, request.feedback_id),
            ("source candidate", result.source_candidate_id, request.source_candidate_id),
            ("domain", result.domain, request.domain),
        )
        for label, actual, expected in checks:
            if actual != expected:
                raise LearningWriteAdaptationOutcomeError(
                    f"adaptation execution {label} identity mismatch"
                )

        if result.status is LearningWriteAdaptationExecutionStatus.COMPLETED:
            fingerprint = self._fingerprint(result.adaptation_result)
            return LearningWriteAdaptationOutcome(
                execution_id=result.execution_id,
                admission_id=result.admission_id,
                proposal_id=result.proposal_id,
                decision_id=result.decision_id,
                candidate_id=result.candidate_id,
                feedback_id=result.feedback_id,
                source_candidate_id=result.source_candidate_id,
                domain=result.domain,
                status=LearningWriteAdaptationOutcomeStatus.SUCCEEDED,
                adaptation_result=result.adaptation_result,
                result_fingerprint=fingerprint,
            )

        return LearningWriteAdaptationOutcome(
            execution_id=result.execution_id,
            admission_id=result.admission_id,
            proposal_id=result.proposal_id,
            decision_id=result.decision_id,
            candidate_id=result.candidate_id,
            feedback_id=result.feedback_id,
            source_candidate_id=result.source_candidate_id,
            domain=result.domain,
            status=LearningWriteAdaptationOutcomeStatus.FAILED,
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
