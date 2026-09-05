"""Execution boundary for admitted learning-write proposals.

This module consumes only an explicitly admitted ``LearningWriteProposal``
and converts the downstream writer response into an immutable result. It
keeps admission, mutation mechanics, authority, authorization, and ordinary
tool execution as distinct concepts.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from typing import Any, Mapping, Protocol

from .learning_write_admission import (
    LearningWriteAdmission,
    LearningWriteAdmissionStatus,
)
from .learning_write_proposal import LearningWriteProposal


class LearningWriteExecutionError(ValueError):
    """Raised when the learning-write execution contract is invalid."""


class LearningWriteExecutionStatus(str, Enum):
    """Normalized result of one admitted learning-write execution."""

    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class LearningWriteExecutionRequest:
    """Immutable execution request derived from an admitted proposal."""

    execution_id: str
    admission_id: str
    proposal_id: str
    decision_id: str
    candidate_id: str
    domain: str
    payload: Mapping[str, Any]

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
                raise LearningWriteExecutionError(
                    f"{field_name} must be a non-empty string"
                )
        if not isinstance(self.payload, Mapping):
            raise LearningWriteExecutionError("payload must be a mapping")


@dataclass(frozen=True)
class LearningWriteExecutionResult:
    """Immutable result bound to one exact admitted write request."""

    execution_id: str
    admission_id: str
    proposal_id: str
    decision_id: str
    candidate_id: str
    domain: str
    status: LearningWriteExecutionStatus
    write_result: Any = None
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
                raise LearningWriteExecutionError(
                    f"{field_name} must be a non-empty string"
                )
        if not isinstance(self.status, LearningWriteExecutionStatus):
            raise LearningWriteExecutionError(
                "status must be a LearningWriteExecutionStatus member"
            )
        if self.reason is not None and not isinstance(self.reason, str):
            raise LearningWriteExecutionError("reason must be a string or None")
        if self.status is LearningWriteExecutionStatus.COMPLETED:
            if self.reason is not None:
                raise LearningWriteExecutionError(
                    "a completed execution cannot contain a failure reason"
                )
        elif self.status is LearningWriteExecutionStatus.FAILED:
            if self.reason is None or not self.reason.strip():
                raise LearningWriteExecutionError(
                    "a failed execution requires a reason"
                )

    def to_context(self) -> dict[str, object]:
        return {
            "learning_write_execution_id": self.execution_id,
            "learning_write_admission_id": self.admission_id,
            "learning_write_proposal_id": self.proposal_id,
            "learning_decision_id": self.decision_id,
            "learning_candidate_id": self.candidate_id,
            "learning_write_domain": self.domain,
            "learning_write_execution_status": self.status.value,
            "learning_written": self.status is LearningWriteExecutionStatus.COMPLETED,
            "memory_mutated": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
        }


class LearningWriter(Protocol):
    """Provider-neutral downstream writer for an admitted request."""

    def write(self, request: LearningWriteExecutionRequest) -> Any:
        """Apply the exact admitted learning-write request."""


class LearningWriteExecutionService:
    """Execute an admitted learning-write proposal through a replaceable writer."""

    def __init__(self, writer: LearningWriter) -> None:
        if not callable(getattr(writer, "write", None)):
            raise TypeError("writer must provide a write(request) method")
        self._writer = writer

    def execute(
        self,
        admission: LearningWriteAdmission,
        proposal: LearningWriteProposal,
    ) -> LearningWriteExecutionResult:
        if not isinstance(admission, LearningWriteAdmission):
            raise TypeError("admission must be a LearningWriteAdmission")
        if not isinstance(proposal, LearningWriteProposal):
            raise TypeError("proposal must be a LearningWriteProposal")
        if admission.status is not LearningWriteAdmissionStatus.ADMITTED:
            raise LearningWriteExecutionError(
                "only admitted learning-write proposals may be executed"
            )
        if admission.proposal_id != proposal.proposal_id:
            raise LearningWriteExecutionError(
                "admission proposal identity does not match proposal"
            )
        if admission.decision_id != proposal.decision_id:
            raise LearningWriteExecutionError(
                "admission decision identity does not match proposal"
            )
        if admission.candidate_id != proposal.candidate_id:
            raise LearningWriteExecutionError(
                "admission candidate identity does not match proposal"
            )
        if admission.domain.value != proposal.domain.value:
            raise LearningWriteExecutionError(
                "admission domain does not match proposal"
            )

        execution_id = self._execution_id(admission, proposal)
        request = LearningWriteExecutionRequest(
            execution_id=execution_id,
            admission_id=admission.admission_id,
            proposal_id=proposal.proposal_id,
            decision_id=proposal.decision_id,
            candidate_id=proposal.candidate_id,
            domain=proposal.domain.value,
            payload=proposal.payload,
        )
        try:
            result = self._writer.write(request)
        except Exception as exc:  # noqa: BLE001 - execution boundary converts failures to data
            return LearningWriteExecutionResult(
                execution_id=execution_id,
                admission_id=admission.admission_id,
                proposal_id=proposal.proposal_id,
                decision_id=proposal.decision_id,
                candidate_id=proposal.candidate_id,
                domain=proposal.domain.value,
                status=LearningWriteExecutionStatus.FAILED,
                reason=str(exc) or exc.__class__.__name__,
            )

        return LearningWriteExecutionResult(
            execution_id=execution_id,
            admission_id=admission.admission_id,
            proposal_id=proposal.proposal_id,
            decision_id=proposal.decision_id,
            candidate_id=proposal.candidate_id,
            domain=proposal.domain.value,
            status=LearningWriteExecutionStatus.COMPLETED,
            write_result=result,
        )

    @staticmethod
    def _execution_id(
        admission: LearningWriteAdmission,
        proposal: LearningWriteProposal,
    ) -> str:
        payload = json.dumps(
            {
                "admission_id": admission.admission_id,
                "proposal_id": proposal.proposal_id,
                "decision_id": proposal.decision_id,
                "candidate_id": proposal.candidate_id,
                "domain": proposal.domain.value,
                "payload": dict(proposal.payload),
            },
            sort_keys=True,
            default=repr,
            separators=(",", ":"),
        ).encode("utf-8")
        return f"learn-write-exec-{hashlib.sha256(payload).hexdigest()[:24]}"
