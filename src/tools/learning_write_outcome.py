"""Result-integrity boundary after a learning-write execution.

This module validates a ``LearningWriteExecutionResult`` against the exact
``LearningWriteExecutionRequest`` that produced it and normalizes the writer
response into an immutable outcome. It does not retry, re-authorize, revoke,
mutate memory, or treat a completed write as unquestionable truth.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from typing import Any, Mapping

from .learning_write_execution import (
    LearningWriteExecutionRequest,
    LearningWriteExecutionResult,
    LearningWriteExecutionStatus,
)


class LearningWriteOutcomeError(ValueError):
    """Raised when learning-write outcome integrity is invalid."""


class LearningWriteOutcomeStatus(str, Enum):
    """Normalized outcome classification for one learning-write execution."""

    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass(frozen=True)
class LearningWriteOutcome:
    """Immutable outcome bound to one exact learning-write execution."""

    execution_id: str
    admission_id: str
    proposal_id: str
    decision_id: str
    candidate_id: str
    domain: str
    status: LearningWriteOutcomeStatus
    write_result: Any = None
    result_fingerprint: str | None = None
    reason: str | None = None

    def __post_init__(self) -> None:
        for field_name, value in (
            ("execution_id", self.execution_id),
            ("admission_id", self.admission_id),
            ("proposal_id", self.proposal_id),
            ("decision_id", self.decision_id),
            ("candidate_id", self.candidate_id),
            ("domain", self.domain),
        ):
            if not isinstance(value, str) or not value.strip():
                raise LearningWriteOutcomeError(
                    f"{field_name} must be a non-empty string"
                )
        if not isinstance(self.status, LearningWriteOutcomeStatus):
            raise LearningWriteOutcomeError(
                "status must be a LearningWriteOutcomeStatus member"
            )
        if self.result_fingerprint is not None and (
            not isinstance(self.result_fingerprint, str)
            or not self.result_fingerprint.strip()
        ):
            raise LearningWriteOutcomeError(
                "result_fingerprint must be a non-empty string or None"
            )
        if self.reason is not None and not isinstance(self.reason, str):
            raise LearningWriteOutcomeError("reason must be a string or None")
        if self.status is LearningWriteOutcomeStatus.SUCCEEDED:
            if self.reason is not None:
                raise LearningWriteOutcomeError(
                    "a succeeded outcome cannot contain a failure reason"
                )
            if self.result_fingerprint is None:
                raise LearningWriteOutcomeError(
                    "a succeeded outcome requires a result fingerprint"
                )
        elif self.status is LearningWriteOutcomeStatus.FAILED:
            if self.reason is None or not self.reason.strip():
                raise LearningWriteOutcomeError(
                    "a failed outcome requires a reason"
                )

    @property
    def succeeded(self) -> bool:
        return self.status is LearningWriteOutcomeStatus.SUCCEEDED

    def to_context(self) -> dict[str, object]:
        return {
            "learning_write_execution_id": self.execution_id,
            "learning_write_admission_id": self.admission_id,
            "learning_write_proposal_id": self.proposal_id,
            "learning_decision_id": self.decision_id,
            "learning_candidate_id": self.candidate_id,
            "learning_write_domain": self.domain,
            "learning_write_outcome_status": self.status.value,
            "learning_write_succeeded": self.succeeded,
            "learning_write_result_fingerprint": self.result_fingerprint,
            "learning_written": self.succeeded,
            "memory_mutated": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
        }


class LearningWriteOutcomeService:
    """Interpret one execution result against its exact execution request."""

    def interpret(
        self,
        result: LearningWriteExecutionResult,
        request: LearningWriteExecutionRequest,
    ) -> LearningWriteOutcome:
        if not isinstance(result, LearningWriteExecutionResult):
            raise TypeError("result must be a LearningWriteExecutionResult")
        if not isinstance(request, LearningWriteExecutionRequest):
            raise TypeError("request must be a LearningWriteExecutionRequest")

        self._validate_identity(result, request)

        if result.status is LearningWriteExecutionStatus.COMPLETED:
            fingerprint = self._fingerprint(result.write_result)
            return LearningWriteOutcome(
                execution_id=result.execution_id,
                admission_id=request.admission_id,
                proposal_id=request.proposal_id,
                decision_id=request.decision_id,
                candidate_id=request.candidate_id,
                domain=request.domain,
                status=LearningWriteOutcomeStatus.SUCCEEDED,
                write_result=result.write_result,
                result_fingerprint=fingerprint,
            )

        return LearningWriteOutcome(
            execution_id=result.execution_id,
            admission_id=request.admission_id,
            proposal_id=request.proposal_id,
            decision_id=request.decision_id,
            candidate_id=request.candidate_id,
            domain=request.domain,
            status=LearningWriteOutcomeStatus.FAILED,
            reason=result.reason or "learning writer failed",
        )

    @staticmethod
    def _validate_identity(
        result: LearningWriteExecutionResult,
        request: LearningWriteExecutionRequest,
    ) -> None:
        pairs = (
            ("execution", result.execution_id, request.execution_id),
            ("admission", result.admission_id, request.admission_id),
            ("proposal", result.proposal_id, request.proposal_id),
            ("decision", result.decision_id, request.decision_id),
            ("candidate", result.candidate_id, request.candidate_id),
            ("domain", result.domain, request.domain),
        )
        for label, actual, expected in pairs:
            if actual != expected:
                raise LearningWriteOutcomeError(
                    f"{label} identity does not match execution request"
                )

    @staticmethod
    def _fingerprint(value: Any) -> str:
        if value is None:
            serialized = "null"
        else:
            try:
                serialized = json.dumps(
                    value,
                    sort_keys=True,
                    default=repr,
                    separators=(",", ":"),
                )
            except TypeError:
                serialized = repr(value)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
