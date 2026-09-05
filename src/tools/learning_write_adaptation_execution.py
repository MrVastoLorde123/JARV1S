"""Execution boundary for admitted adaptation proposals.

Only an explicitly admitted adaptation proposal may reach the replaceable
applier. Execution results are immutable observations; applying an adaptation
is not authorization, retry, revocation, or proof of truth.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from typing import Any, Mapping, Protocol

from .learning_write_adaptation_admission import (
    LearningWriteAdaptationAdmission,
    LearningWriteAdaptationAdmissionStatus,
)
from .learning_write_adaptation_proposal import LearningWriteAdaptationProposal


class LearningWriteAdaptationExecutionError(ValueError):
    """Raised when the adaptation-execution contract is invalid."""


class LearningWriteAdaptationExecutionStatus(str, Enum):
    """Normalized result of one admitted adaptation execution."""

    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class LearningWriteAdaptationExecutionRequest:
    """Immutable execution request derived from an admitted proposal."""

    execution_id: str
    admission_id: str
    proposal_id: str
    decision_id: str
    candidate_id: str
    feedback_id: str
    source_candidate_id: str
    domain: str
    adaptation: Mapping[str, Any]

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
                raise LearningWriteAdaptationExecutionError(
                    f"{field_name} must be a non-empty string"
                )
        if not isinstance(self.adaptation, Mapping):
            raise LearningWriteAdaptationExecutionError("adaptation must be a mapping")


@dataclass(frozen=True)
class LearningWriteAdaptationExecutionResult:
    """Immutable result bound to one exact admitted adaptation request."""

    execution_id: str
    admission_id: str
    proposal_id: str
    decision_id: str
    candidate_id: str
    feedback_id: str
    source_candidate_id: str
    domain: str
    status: LearningWriteAdaptationExecutionStatus
    adaptation_result: Any = None
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
                raise LearningWriteAdaptationExecutionError(
                    f"{field_name} must be a non-empty string"
                )
        if not isinstance(self.status, LearningWriteAdaptationExecutionStatus):
            raise LearningWriteAdaptationExecutionError(
                "status must be a LearningWriteAdaptationExecutionStatus member"
            )
        if self.reason is not None and not isinstance(self.reason, str):
            raise LearningWriteAdaptationExecutionError("reason must be a string or None")
        if self.status is LearningWriteAdaptationExecutionStatus.COMPLETED and self.reason is not None:
            raise LearningWriteAdaptationExecutionError(
                "a completed adaptation execution cannot contain a failure reason"
            )
        if self.status is LearningWriteAdaptationExecutionStatus.FAILED and (
            self.reason is None or not self.reason.strip()
        ):
            raise LearningWriteAdaptationExecutionError(
                "a failed adaptation execution requires a reason"
            )

    def to_context(self) -> dict[str, object]:
        return {
            "learning_write_adaptation_execution_id": self.execution_id,
            "learning_write_adaptation_admission_id": self.admission_id,
            "learning_write_adaptation_proposal_id": self.proposal_id,
            "learning_write_adaptation_decision_id": self.decision_id,
            "learning_write_feedback_id": self.feedback_id,
            "learning_candidate_id": self.source_candidate_id,
            "learning_write_adaptation_domain": self.domain,
            "learning_write_adaptation_execution_status": self.status.value,
            "adaptation_applied": self.status is LearningWriteAdaptationExecutionStatus.COMPLETED,
            "learning_written": False,
            "memory_mutated": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
        }


class LearningWriteAdaptationApplier(Protocol):
    """Provider-neutral downstream applier for an admitted adaptation."""

    def apply(self, request: LearningWriteAdaptationExecutionRequest) -> Any:
        """Apply the exact admitted adaptation request."""


class LearningWriteAdaptationExecutionService:
    """Execute an admitted adaptation proposal through a replaceable applier."""

    def __init__(self, applier: LearningWriteAdaptationApplier) -> None:
        if not callable(getattr(applier, "apply", None)):
            raise TypeError("applier must provide an apply(request) method")
        self._applier = applier

    def execute(
        self,
        admission: LearningWriteAdaptationAdmission,
        proposal: LearningWriteAdaptationProposal,
    ) -> LearningWriteAdaptationExecutionResult:
        if not isinstance(admission, LearningWriteAdaptationAdmission):
            raise TypeError("admission must be a LearningWriteAdaptationAdmission")
        if not isinstance(proposal, LearningWriteAdaptationProposal):
            raise TypeError("proposal must be a LearningWriteAdaptationProposal")
        if admission.status is not LearningWriteAdaptationAdmissionStatus.ADMITTED:
            raise LearningWriteAdaptationExecutionError(
                "only admitted adaptation proposals may be executed"
            )

        checks = (
            ("proposal", admission.proposal_id, proposal.proposal_id),
            ("decision", admission.decision_id, proposal.decision_id),
            ("candidate", admission.candidate_id, proposal.candidate_id),
            ("feedback", admission.feedback_id, proposal.feedback_id),
            ("execution", admission.execution_id, proposal.execution_id),
            ("domain", admission.domain, proposal.domain),
        )
        for label, expected, actual in checks:
            expected_value = expected.value if hasattr(expected, "value") else expected
            actual_value = actual.value if hasattr(actual, "value") else actual
            if expected_value != actual_value:
                raise LearningWriteAdaptationExecutionError(
                    f"admission {label} identity does not match proposal"
                )

        execution_id = self._execution_id(admission, proposal)
        request = LearningWriteAdaptationExecutionRequest(
            execution_id=execution_id,
            admission_id=admission.admission_id,
            proposal_id=proposal.proposal_id,
            decision_id=proposal.decision_id,
            candidate_id=proposal.candidate_id,
            feedback_id=proposal.feedback_id,
            source_candidate_id=proposal.proposal_source_candidate_id,
            domain=proposal.domain,
            adaptation=proposal.adaptation,
        )
        try:
            result = self._applier.apply(request)
        except Exception as exc:  # noqa: BLE001 - execution boundary converts failures to data
            return LearningWriteAdaptationExecutionResult(
                execution_id=execution_id,
                admission_id=admission.admission_id,
                proposal_id=proposal.proposal_id,
                decision_id=proposal.decision_id,
                candidate_id=proposal.candidate_id,
                feedback_id=proposal.feedback_id,
                source_candidate_id=proposal.proposal_source_candidate_id,
                domain=proposal.domain,
                status=LearningWriteAdaptationExecutionStatus.FAILED,
                reason=str(exc) or exc.__class__.__name__,
            )

        return LearningWriteAdaptationExecutionResult(
            execution_id=execution_id,
            admission_id=admission.admission_id,
            proposal_id=proposal.proposal_id,
            decision_id=proposal.decision_id,
            candidate_id=proposal.candidate_id,
            feedback_id=proposal.feedback_id,
            source_candidate_id=proposal.proposal_source_candidate_id,
            domain=proposal.domain,
            status=LearningWriteAdaptationExecutionStatus.COMPLETED,
            adaptation_result=result,
        )

    @staticmethod
    def _execution_id(
        admission: LearningWriteAdaptationAdmission,
        proposal: LearningWriteAdaptationProposal,
    ) -> str:
        payload = json.dumps(
            {
                "admission_id": admission.admission_id,
                "proposal_id": proposal.proposal_id,
                "decision_id": proposal.decision_id,
                "candidate_id": proposal.candidate_id,
                "feedback_id": proposal.feedback_id,
                "source_candidate_id": proposal.proposal_source_candidate_id,
                "domain": proposal.domain,
                "adaptation": dict(proposal.adaptation),
            },
            sort_keys=True,
            default=repr,
            separators=(",", ":"),
        ).encode("utf-8")
        return f"learn-write-adaptation-exec-{hashlib.sha256(payload).hexdigest()[:24]}"
