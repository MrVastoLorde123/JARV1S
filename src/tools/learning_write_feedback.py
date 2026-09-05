"""Feedback boundary after a learning-write outcome.

This module converts a verified learning-write outcome into inert feedback
that can later be evaluated. It does not write memory, authorize, retry,
revoke, or execute tools.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping

from .learning_write_outcome import LearningWriteOutcome, LearningWriteOutcomeStatus


class LearningWriteFeedbackError(ValueError):
    """Raised when the learning-write feedback contract is invalid."""


class LearningWriteFeedbackKind(str, Enum):
    """Normalized feedback classification for a learning-write outcome."""

    WRITE_SUCCESS = "write_success"
    WRITE_FAILURE = "write_failure"


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
class LearningWriteFeedbackEvent:
    """Immutable feedback evidence derived from one learning-write outcome."""

    feedback_id: str
    execution_id: str
    admission_id: str
    proposal_id: str
    decision_id: str
    candidate_id: str
    domain: str
    kind: LearningWriteFeedbackKind
    payload: Mapping[str, Any]
    provenance: Mapping[str, str]
    reason: str

    def __post_init__(self) -> None:
        for field_name, value in (
            ("feedback_id", self.feedback_id),
            ("execution_id", self.execution_id),
            ("admission_id", self.admission_id),
            ("proposal_id", self.proposal_id),
            ("decision_id", self.decision_id),
            ("candidate_id", self.candidate_id),
            ("domain", self.domain),
            ("reason", self.reason),
        ):
            if not isinstance(value, str) or not value.strip():
                raise LearningWriteFeedbackError(f"{field_name} must be a non-empty string")
        if not isinstance(self.kind, LearningWriteFeedbackKind):
            raise LearningWriteFeedbackError("kind must be a LearningWriteFeedbackKind member")
        if not isinstance(self.payload, Mapping):
            raise LearningWriteFeedbackError("payload must be a mapping")
        if not isinstance(self.provenance, Mapping):
            raise LearningWriteFeedbackError("provenance must be a mapping")
        if not all(
            isinstance(key, str) and key.strip()
            and isinstance(value, str) and value.strip()
            for key, value in self.provenance.items()
        ):
            raise LearningWriteFeedbackError(
                "provenance must contain non-empty string keys and values"
            )
        object.__setattr__(self, "payload", _freeze(self.payload))
        object.__setattr__(self, "provenance", _freeze(self.provenance))

    def to_context(self) -> dict[str, object]:
        return {
            "learning_write_feedback_id": self.feedback_id,
            "learning_write_execution_id": self.execution_id,
            "learning_write_admission_id": self.admission_id,
            "learning_write_proposal_id": self.proposal_id,
            "learning_decision_id": self.decision_id,
            "learning_candidate_id": self.candidate_id,
            "learning_write_domain": self.domain,
            "learning_write_feedback_kind": self.kind.value,
            "payload": dict(self.payload),
            "provenance": dict(self.provenance),
            "learning_write_feedback_reason": self.reason,
            "learning_written": self.kind is LearningWriteFeedbackKind.WRITE_SUCCESS,
            "memory_mutated": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
        }


class LearningWriteFeedbackService:
    """Convert a learning-write outcome into inert feedback evidence."""

    def from_outcome(self, outcome: LearningWriteOutcome) -> LearningWriteFeedbackEvent:
        if not isinstance(outcome, LearningWriteOutcome):
            raise TypeError("outcome must be a LearningWriteOutcome")

        if outcome.status is LearningWriteOutcomeStatus.SUCCEEDED:
            kind = LearningWriteFeedbackKind.WRITE_SUCCESS
            payload = {
                "outcome_status": outcome.status.value,
                "write_result": outcome.write_result,
                "result_fingerprint": outcome.result_fingerprint,
            }
            reason = "learning write completed and produced observable write feedback"
        else:
            kind = LearningWriteFeedbackKind.WRITE_FAILURE
            payload = {
                "outcome_status": outcome.status.value,
                "reason": outcome.reason,
            }
            reason = "learning write failed and produced observable failure feedback"

        provenance = {
            "source": "learning_write_outcome",
            "execution_id": outcome.execution_id,
            "admission_id": outcome.admission_id,
            "proposal_id": outcome.proposal_id,
            "decision_id": outcome.decision_id,
            "candidate_id": outcome.candidate_id,
        }
        feedback_id = self._feedback_id(outcome, kind, payload)
        return LearningWriteFeedbackEvent(
            feedback_id=feedback_id,
            execution_id=outcome.execution_id,
            admission_id=outcome.admission_id,
            proposal_id=outcome.proposal_id,
            decision_id=outcome.decision_id,
            candidate_id=outcome.candidate_id,
            domain=outcome.domain,
            kind=kind,
            payload=payload,
            provenance=provenance,
            reason=reason,
        )

    @staticmethod
    def _feedback_id(
        outcome: LearningWriteOutcome,
        kind: LearningWriteFeedbackKind,
        payload: Mapping[str, Any],
    ) -> str:
        serialized = json.dumps(
            {
                "execution_id": outcome.execution_id,
                "admission_id": outcome.admission_id,
                "proposal_id": outcome.proposal_id,
                "decision_id": outcome.decision_id,
                "candidate_id": outcome.candidate_id,
                "domain": outcome.domain,
                "kind": kind.value,
                "payload": payload,
            },
            sort_keys=True,
            default=repr,
            separators=(",", ":"),
        ).encode("utf-8")
        return f"learn-write-feedback-{hashlib.sha256(serialized).hexdigest()[:24]}"
