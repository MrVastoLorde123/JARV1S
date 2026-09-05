"""Feedback boundary after future adaptation execution result integrity.

M22.44 converts exactly one M22.43 result-integrity outcome into immutable
feedback evidence. Feedback preserves the complete known lineage and the
observed execution evidence, but it does not authorize, execute, retry,
revoke, mutate memory, or establish adaptation truth.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping

from .learning_write_adaptation_evaluation_execution_feedback_result_integrity import (
    LearningWriteAdaptationEvaluationExecutionFeedbackOutcome,
    LearningWriteAdaptationEvaluationExecutionFeedbackOutcomeStatus,
)


class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackError(ValueError):
    """Raised when the M22.44 feedback contract is invalid."""


class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackKind(str, Enum):
    """Feedback classification for one exact M22.43 integrity outcome."""

    INTEGRITY_SUCCESS = "integrity_success"
    INTEGRITY_FAILURE = "integrity_failure"


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
class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedback:
    """Immutable feedback evidence derived from one exact M22.43 outcome."""

    feedback_id: str
    outcome_id: str
    execution_id: str
    preparation_id: str
    admission_id: str
    proposal_id: str
    decision_id: str
    evaluation_id: str
    decision_source_evaluation_id: str
    source_feedback_id: str
    candidate_id: str
    source_candidate_id: str
    execution_source_id: str
    source_execution_id: str
    source_admission_id: str
    proposal_source_id: str
    domain: str
    source_policy_id: str
    policy_id: str
    kind: LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackKind
    payload: Mapping[str, Any]
    provenance: Mapping[str, str]
    reason: str

    def __post_init__(self) -> None:
        for field_name, value in (
            ("feedback_id", self.feedback_id),
            ("outcome_id", self.outcome_id),
            ("execution_id", self.execution_id),
            ("preparation_id", self.preparation_id),
            ("admission_id", self.admission_id),
            ("proposal_id", self.proposal_id),
            ("decision_id", self.decision_id),
            ("evaluation_id", self.evaluation_id),
            ("decision_source_evaluation_id", self.decision_source_evaluation_id),
            ("source_feedback_id", self.source_feedback_id),
            ("candidate_id", self.candidate_id),
            ("source_candidate_id", self.source_candidate_id),
            ("execution_source_id", self.execution_source_id),
            ("source_execution_id", self.source_execution_id),
            ("source_admission_id", self.source_admission_id),
            ("proposal_source_id", self.proposal_source_id),
            ("domain", self.domain),
            ("source_policy_id", self.source_policy_id),
            ("policy_id", self.policy_id),
            ("reason", self.reason),
        ):
            if not isinstance(value, str) or not value.strip():
                raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackError(
                    f"{field_name} must be a non-empty string"
                )
        if not isinstance(
            self.kind,
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackKind,
        ):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackError(
                "kind must be a LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackKind member"
            )
        if not isinstance(self.payload, Mapping):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackError(
                "payload must be a mapping"
            )
        if not isinstance(self.provenance, Mapping):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackError(
                "provenance must be a mapping"
            )
        if not all(
            isinstance(key, str) and key.strip() and isinstance(value, str) and value.strip()
            for key, value in self.provenance.items()
        ):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackError(
                "provenance must contain non-empty string keys and values"
            )
        object.__setattr__(self, "payload", _freeze(self.payload))
        object.__setattr__(self, "provenance", _freeze(self.provenance))

    def to_context(self) -> dict[str, object]:
        return {
            "learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_id": self.feedback_id,
            "learning_write_adaptation_evaluation_execution_feedback_outcome_id": self.outcome_id,
            "learning_write_adaptation_evaluation_execution_id": self.execution_id,
            "learning_write_adaptation_evaluation_execution_preparation_id": self.preparation_id,
            "learning_write_adaptation_evaluation_execution_feedback_proposal_admission_id": self.admission_id,
            "learning_write_adaptation_evaluation_execution_feedback_proposal_id": self.proposal_id,
            "learning_write_adaptation_evaluation_execution_feedback_decision_id": self.decision_id,
            "learning_write_adaptation_evaluation_execution_feedback_evaluation_id": self.evaluation_id,
            "learning_write_adaptation_feedback_evaluation_id": self.decision_source_evaluation_id,
            "learning_write_adaptation_evaluation_execution_feedback_id": self.source_feedback_id,
            "learning_write_adaptation_candidate_id": self.candidate_id,
            "learning_candidate_id": self.source_candidate_id,
            "learning_write_adaptation_evaluation_execution_source_id": self.execution_source_id,
            "learning_write_adaptation_source_execution_id": self.source_execution_id,
            "learning_write_adaptation_evaluation_execution_source_admission_id": self.source_admission_id,
            "learning_write_adaptation_evaluation_proposal_id": self.proposal_source_id,
            "learning_write_adaptation_domain": self.domain,
            "learning_write_adaptation_source_policy_id": self.source_policy_id,
            "learning_write_adaptation_evaluation_execution_policy_id": self.policy_id,
            "learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_kind": self.kind.value,
            "payload": dict(self.payload),
            "provenance": dict(self.provenance),
            "learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_reason": self.reason,
            "result_integrity_feedback_observed": True,
            "adaptation_truth_proven": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
            "memory_mutation_allowed": False,
        }


class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackService:
    """Convert one M22.43 integrity outcome into inert feedback evidence."""

    def from_outcome(
        self,
        outcome: LearningWriteAdaptationEvaluationExecutionFeedbackOutcome,
    ) -> LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedback:
        if not isinstance(
            outcome,
            LearningWriteAdaptationEvaluationExecutionFeedbackOutcome,
        ):
            raise TypeError(
                "outcome must be a LearningWriteAdaptationEvaluationExecutionFeedbackOutcome"
            )

        if outcome.status is LearningWriteAdaptationEvaluationExecutionFeedbackOutcomeStatus.SUCCEEDED:
            kind = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackKind.INTEGRITY_SUCCESS
            payload = {
                "outcome_status": outcome.status.value,
                "execution_result": outcome.execution_result,
                "result_fingerprint": outcome.result_fingerprint,
            }
            reason = "successful result-integrity evidence provides observable future adaptation execution feedback"
        elif outcome.status is LearningWriteAdaptationEvaluationExecutionFeedbackOutcomeStatus.FAILED:
            kind = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackKind.INTEGRITY_FAILURE
            payload = {
                "outcome_status": outcome.status.value,
                "reason": outcome.reason,
            }
            reason = "failed result-integrity evidence provides observable future adaptation execution feedback"
        else:
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackError(
                "unsupported future adaptation execution result-integrity outcome status"
            )

        provenance = {
            "source": "learning_write_adaptation_evaluation_execution_feedback_result_integrity",
            "outcome_id": outcome.execution_id,
            "execution_id": outcome.execution_id,
            "preparation_id": outcome.preparation_id,
            "admission_id": outcome.admission_id,
            "proposal_id": outcome.proposal_id,
            "decision_id": outcome.decision_id,
            "evaluation_id": outcome.evaluation_id,
            "decision_source_evaluation_id": outcome.decision_source_evaluation_id,
            "source_feedback_id": outcome.source_feedback_id,
            "candidate_id": outcome.candidate_id,
            "source_candidate_id": outcome.source_candidate_id,
            "execution_source_id": outcome.execution_source_id,
            "source_execution_id": outcome.source_execution_id,
            "source_admission_id": outcome.source_admission_id,
            "proposal_source_id": outcome.proposal_source_id,
            "domain": outcome.domain,
            "source_policy_id": outcome.source_policy_id,
            "policy_id": outcome.policy_id,
        }
        feedback_id = self._feedback_id(outcome, kind, payload)
        return LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedback(
            feedback_id=feedback_id,
            outcome_id=outcome.execution_id,
            execution_id=outcome.execution_id,
            preparation_id=outcome.preparation_id,
            admission_id=outcome.admission_id,
            proposal_id=outcome.proposal_id,
            decision_id=outcome.decision_id,
            evaluation_id=outcome.evaluation_id,
            decision_source_evaluation_id=outcome.decision_source_evaluation_id,
            source_feedback_id=outcome.source_feedback_id,
            candidate_id=outcome.candidate_id,
            source_candidate_id=outcome.source_candidate_id,
            execution_source_id=outcome.execution_source_id,
            source_execution_id=outcome.source_execution_id,
            source_admission_id=outcome.source_admission_id,
            proposal_source_id=outcome.proposal_source_id,
            domain=outcome.domain,
            source_policy_id=outcome.source_policy_id,
            policy_id=outcome.policy_id,
            kind=kind,
            payload=payload,
            provenance=provenance,
            reason=reason,
        )

    @staticmethod
    def _feedback_id(
        outcome: LearningWriteAdaptationEvaluationExecutionFeedbackOutcome,
        kind: LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackKind,
        payload: Mapping[str, Any],
    ) -> str:
        serialized = json.dumps(
            {
                "source_outcome_id": outcome.execution_id,
                "preparation_id": outcome.preparation_id,
                "admission_id": outcome.admission_id,
                "proposal_id": outcome.proposal_id,
                "decision_id": outcome.decision_id,
                "evaluation_id": outcome.evaluation_id,
                "decision_source_evaluation_id": outcome.decision_source_evaluation_id,
                "source_feedback_id": outcome.source_feedback_id,
                "candidate_id": outcome.candidate_id,
                "source_candidate_id": outcome.source_candidate_id,
                "execution_source_id": outcome.execution_source_id,
                "source_execution_id": outcome.source_execution_id,
                "source_admission_id": outcome.source_admission_id,
                "proposal_source_id": outcome.proposal_source_id,
                "domain": outcome.domain,
                "source_policy_id": outcome.source_policy_id,
                "policy_id": outcome.policy_id,
                "kind": kind.value,
                "payload": payload,
            },
            sort_keys=True,
            default=repr,
            separators=(",", ":"),
        ).encode("utf-8")
        return (
            "adaptation-evaluation-execution-feedback-result-integrity-feedback-"
            f"{hashlib.sha256(serialized).hexdigest()[:24]}"
        )
