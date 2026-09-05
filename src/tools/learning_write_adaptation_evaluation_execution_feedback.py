"""Feedback boundary after future adaptation execution result integrity.

This module converts one M22.35 result-integrity outcome into immutable
feedback for later evaluation. It preserves exact lineage and does not
authorize, execute, retry, revoke, or mutate memory.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping

from .learning_write_adaptation_evaluation_execution_result import (
    LearningWriteAdaptationEvaluationExecutionOutcome,
    LearningWriteAdaptationEvaluationExecutionOutcomeStatus,
)


class LearningWriteAdaptationEvaluationExecutionFeedbackError(ValueError):
    """Raised when the M22.36 feedback contract is invalid."""


class LearningWriteAdaptationEvaluationExecutionFeedbackKind(str, Enum):
    """Normalized feedback classification for one M22.35 outcome."""

    EXECUTION_SUCCESS = "execution_success"
    EXECUTION_FAILURE = "execution_failure"


def _freeze(value: Any) -> Any:
    """Recursively freeze common mutable containers into immutable snapshots."""
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
class LearningWriteAdaptationEvaluationExecutionFeedback:
    """Immutable feedback evidence derived from one exact M22.35 outcome."""

    feedback_id: str
    execution_id: str
    preparation_id: str
    admission_id: str
    proposal_id: str
    decision_id: str
    evaluation_id: str
    source_feedback_id: str
    candidate_id: str
    source_candidate_id: str
    source_execution_id: str
    domain: str
    policy_id: str
    kind: LearningWriteAdaptationEvaluationExecutionFeedbackKind
    payload: Mapping[str, Any]
    provenance: Mapping[str, str]
    reason: str

    def __post_init__(self) -> None:
        for field_name, value in (
            ("feedback_id", self.feedback_id), ("execution_id", self.execution_id),
            ("preparation_id", self.preparation_id), ("admission_id", self.admission_id),
            ("proposal_id", self.proposal_id), ("decision_id", self.decision_id),
            ("evaluation_id", self.evaluation_id), ("source_feedback_id", self.source_feedback_id),
            ("candidate_id", self.candidate_id), ("source_candidate_id", self.source_candidate_id),
            ("source_execution_id", self.source_execution_id), ("domain", self.domain),
            ("policy_id", self.policy_id), ("reason", self.reason),
        ):
            if not isinstance(value, str) or not value.strip():
                raise LearningWriteAdaptationEvaluationExecutionFeedbackError(
                    f"{field_name} must be a non-empty string"
                )
        if not isinstance(self.kind, LearningWriteAdaptationEvaluationExecutionFeedbackKind):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackError(
                "kind must be a LearningWriteAdaptationEvaluationExecutionFeedbackKind member"
            )
        if not isinstance(self.payload, Mapping):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackError("payload must be a mapping")
        if not isinstance(self.provenance, Mapping):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackError("provenance must be a mapping")
        if not all(
            isinstance(key, str) and key.strip() and isinstance(value, str) and value.strip()
            for key, value in self.provenance.items()
        ):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackError(
                "provenance must contain non-empty string keys and values"
            )
        object.__setattr__(self, "payload", _freeze(self.payload))
        object.__setattr__(self, "provenance", _freeze(self.provenance))

    def to_context(self) -> dict[str, object]:
        return {
            "learning_write_adaptation_evaluation_execution_feedback_id": self.feedback_id,
            "learning_write_adaptation_evaluation_execution_outcome_id": self.execution_id,
            "learning_write_adaptation_evaluation_execution_id": self.execution_id,
            "learning_write_adaptation_evaluation_execution_preparation_id": self.preparation_id,
            "learning_write_adaptation_evaluation_proposal_admission_id": self.admission_id,
            "learning_write_adaptation_evaluation_proposal_id": self.proposal_id,
            "learning_write_adaptation_evaluation_decision_id": self.decision_id,
            "learning_write_adaptation_feedback_evaluation_id": self.evaluation_id,
            "learning_write_adaptation_source_feedback_id": self.source_feedback_id,
            "learning_write_adaptation_candidate_id": self.candidate_id,
            "learning_candidate_id": self.source_candidate_id,
            "learning_write_adaptation_source_execution_id": self.source_execution_id,
            "learning_write_adaptation_domain": self.domain,
            "learning_write_adaptation_evaluation_execution_policy_id": self.policy_id,
            "learning_write_adaptation_evaluation_execution_feedback_kind": self.kind.value,
            "payload": dict(self.payload),
            "provenance": dict(self.provenance),
            "learning_write_adaptation_evaluation_execution_feedback_reason": self.reason,
            "execution_feedback_observed": True,
            "authority_granted": False, "authorization_granted": False,
            "execution_requested": False, "retry_requested": False,
            "revocation_requested": False, "memory_mutation_allowed": False,
        }


class LearningWriteAdaptationEvaluationExecutionFeedbackService:
    """Convert one M22.35 outcome into inert feedback evidence."""

    def from_outcome(self, outcome: LearningWriteAdaptationEvaluationExecutionOutcome) -> LearningWriteAdaptationEvaluationExecutionFeedback:
        if not isinstance(outcome, LearningWriteAdaptationEvaluationExecutionOutcome):
            raise TypeError("outcome must be a LearningWriteAdaptationEvaluationExecutionOutcome")
        if outcome.status is LearningWriteAdaptationEvaluationExecutionOutcomeStatus.SUCCEEDED:
            kind = LearningWriteAdaptationEvaluationExecutionFeedbackKind.EXECUTION_SUCCESS
            payload = {"outcome_status": outcome.status.value, "execution_result": outcome.execution_result, "result_fingerprint": outcome.result_fingerprint}
            reason = "successful future adaptation execution outcome provides observable execution feedback"
        elif outcome.status is LearningWriteAdaptationEvaluationExecutionOutcomeStatus.FAILED:
            kind = LearningWriteAdaptationEvaluationExecutionFeedbackKind.EXECUTION_FAILURE
            payload = {"outcome_status": outcome.status.value, "reason": outcome.reason}
            reason = "failed future adaptation execution outcome provides observable operational feedback"
        else:
            raise LearningWriteAdaptationEvaluationExecutionFeedbackError("unsupported future adaptation execution outcome status")
        provenance = {
            "source": "learning_write_adaptation_evaluation_execution_result",
            "outcome_id": outcome.execution_id, "execution_id": outcome.execution_id,
            "preparation_id": outcome.preparation_id, "admission_id": outcome.admission_id,
            "proposal_id": outcome.proposal_id, "decision_id": outcome.decision_id,
            "evaluation_id": outcome.evaluation_id, "feedback_id": outcome.feedback_id,
            "source_feedback_id": outcome.source_feedback_id, "candidate_id": outcome.candidate_id,
            "source_candidate_id": outcome.source_candidate_id, "source_execution_id": outcome.source_execution_id,
            "domain": outcome.domain, "policy_id": outcome.policy_id,
        }
        feedback_id = self._feedback_id(outcome, kind, payload)
        return LearningWriteAdaptationEvaluationExecutionFeedback(
            feedback_id=feedback_id, execution_id=outcome.execution_id,
            preparation_id=outcome.preparation_id, admission_id=outcome.admission_id,
            proposal_id=outcome.proposal_id, decision_id=outcome.decision_id,
            evaluation_id=outcome.evaluation_id, source_feedback_id=outcome.source_feedback_id,
            candidate_id=outcome.candidate_id, source_candidate_id=outcome.source_candidate_id,
            source_execution_id=outcome.source_execution_id, domain=outcome.domain,
            policy_id=outcome.policy_id, kind=kind, payload=payload,
            provenance=provenance, reason=reason,
        )

    @staticmethod
    def _feedback_id(outcome: LearningWriteAdaptationEvaluationExecutionOutcome, kind: LearningWriteAdaptationEvaluationExecutionFeedbackKind, payload: Mapping[str, Any]) -> str:
        serialized = json.dumps({
            "source_outcome_id": outcome.execution_id, "preparation_id": outcome.preparation_id,
            "admission_id": outcome.admission_id, "proposal_id": outcome.proposal_id,
            "decision_id": outcome.decision_id, "evaluation_id": outcome.evaluation_id,
            "source_feedback_id": outcome.source_feedback_id, "candidate_id": outcome.candidate_id,
            "source_candidate_id": outcome.source_candidate_id, "source_execution_id": outcome.source_execution_id,
            "domain": outcome.domain, "policy_id": outcome.policy_id, "kind": kind.value, "payload": payload,
        }, sort_keys=True, default=repr, separators=(",", ":")).encode("utf-8")
        return f"adaptation-evaluation-execution-feedback-{hashlib.sha256(serialized).hexdigest()[:24]}"
