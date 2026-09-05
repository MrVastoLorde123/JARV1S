"""Execution boundary after future-adaptation feedback preparation.

An immutable M22.41 preparation artifact may cross into an execution attempt
through a replaceable applier. Execution is observational and non-authorizing;
it does not create retry, revocation, or memory-mutation authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping, Protocol

from .learning_write_adaptation_evaluation_execution_feedback_preparation import (
    LearningWriteAdaptationEvaluationExecutionFeedbackPreparation,
)


class LearningWriteAdaptationEvaluationExecutionFeedbackExecutionError(ValueError):
    """Raised when the M22.42 execution contract is invalid."""


class LearningWriteAdaptationEvaluationExecutionFeedbackExecutionStatus(str, Enum):
    """Normalized result of one future adaptation execution attempt."""

    COMPLETED = "completed"
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
class LearningWriteAdaptationEvaluationExecutionFeedbackExecutionRequest:
    """Immutable execution request derived from one exact preparation artifact."""

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
    execution_source_id: str
    source_execution_id: str
    source_admission_id: str
    proposal_source_id: str
    domain: str
    source_policy_id: str
    policy_id: str
    payload: Mapping[str, Any]
    evidence: Mapping[str, Any]
    provenance: Mapping[str, str]

    def __post_init__(self) -> None:
        for field_name, value in (
            ("execution_id", self.execution_id),
            ("preparation_id", self.preparation_id),
            ("admission_id", self.admission_id),
            ("proposal_id", self.proposal_id),
            ("decision_id", self.decision_id),
            ("evaluation_id", self.evaluation_id),
            ("decision_source_evaluation_id", self.decision_source_evaluation_id),
            ("feedback_id", self.feedback_id),
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
        ):
            if not isinstance(value, str) or not value.strip():
                raise LearningWriteAdaptationEvaluationExecutionFeedbackExecutionError(
                    f"{field_name} must be a non-empty string"
                )
        for field_name, value in (("payload", self.payload), ("evidence", self.evidence)):
            if not isinstance(value, Mapping):
                raise LearningWriteAdaptationEvaluationExecutionFeedbackExecutionError(
                    f"{field_name} must be a mapping"
                )
        if not isinstance(self.provenance, Mapping):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackExecutionError(
                "provenance must be a mapping"
            )
        object.__setattr__(self, "payload", _freeze(self.payload))
        object.__setattr__(self, "evidence", _freeze(self.evidence))
        object.__setattr__(self, "provenance", _freeze(self.provenance))


@dataclass(frozen=True)
class LearningWriteAdaptationEvaluationExecutionFeedbackExecutionResult:
    """Immutable execution attempt result bound to one exact preparation."""

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
    execution_source_id: str
    source_execution_id: str
    source_admission_id: str
    proposal_source_id: str
    domain: str
    source_policy_id: str
    policy_id: str
    status: LearningWriteAdaptationEvaluationExecutionFeedbackExecutionStatus
    execution_result: Any = None
    reason: str | None = None

    def __post_init__(self) -> None:
        for field_name, value in (
            ("execution_id", self.execution_id),
            ("preparation_id", self.preparation_id),
            ("admission_id", self.admission_id),
            ("proposal_id", self.proposal_id),
            ("decision_id", self.decision_id),
            ("evaluation_id", self.evaluation_id),
            ("decision_source_evaluation_id", self.decision_source_evaluation_id),
            ("feedback_id", self.feedback_id),
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
        ):
            if not isinstance(value, str) or not value.strip():
                raise LearningWriteAdaptationEvaluationExecutionFeedbackExecutionError(
                    f"{field_name} must be a non-empty string"
                )
        if not isinstance(
            self.status,
            LearningWriteAdaptationEvaluationExecutionFeedbackExecutionStatus,
        ):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackExecutionError(
                "status must be a LearningWriteAdaptationEvaluationExecutionFeedbackExecutionStatus member"
            )
        if self.status is LearningWriteAdaptationEvaluationExecutionFeedbackExecutionStatus.COMPLETED:
            if self.reason is not None:
                raise LearningWriteAdaptationEvaluationExecutionFeedbackExecutionError(
                    "a completed execution cannot contain a failure reason"
                )
        elif not isinstance(self.reason, str) or not self.reason.strip():
            raise LearningWriteAdaptationEvaluationExecutionFeedbackExecutionError(
                "a failed execution requires a non-empty reason"
            )

    def to_context(self) -> dict[str, object]:
        return {
            "learning_write_adaptation_evaluation_execution_feedback_execution_id": self.execution_id,
            "learning_write_adaptation_evaluation_execution_feedback_preparation_id": self.preparation_id,
            "learning_write_adaptation_evaluation_execution_feedback_proposal_admission_id": self.admission_id,
            "learning_write_adaptation_evaluation_execution_feedback_proposal_id": self.proposal_id,
            "learning_write_adaptation_evaluation_execution_feedback_decision_id": self.decision_id,
            "learning_write_adaptation_evaluation_execution_feedback_evaluation_id": self.evaluation_id,
            "learning_write_adaptation_feedback_evaluation_id": self.decision_source_evaluation_id,
            "learning_write_adaptation_evaluation_execution_feedback_id": self.feedback_id,
            "learning_write_adaptation_source_feedback_id": self.source_feedback_id,
            "learning_write_adaptation_candidate_id": self.candidate_id,
            "learning_candidate_id": self.source_candidate_id,
            "learning_write_adaptation_evaluation_execution_source_id": self.execution_source_id,
            "learning_write_adaptation_source_execution_id": self.source_execution_id,
            "learning_write_adaptation_evaluation_execution_source_admission_id": self.source_admission_id,
            "learning_write_adaptation_evaluation_proposal_id": self.proposal_source_id,
            "learning_write_adaptation_domain": self.domain,
            "learning_write_adaptation_source_policy_id": self.source_policy_id,
            "learning_write_adaptation_evaluation_execution_policy_id": self.policy_id,
            "learning_write_adaptation_evaluation_execution_feedback_status": self.status.value,
            "execution_completed": self.status is LearningWriteAdaptationEvaluationExecutionFeedbackExecutionStatus.COMPLETED,
            "authorization_granted": False,
            "retry_requested": False,
            "revocation_requested": False,
            "memory_mutation_allowed": False,
            "authority_granted": False,
        }


class LearningWriteAdaptationEvaluationExecutionFeedbackExecutionApplier(Protocol):
    """Replaceable applier for the exact future execution request."""

    def apply(self, request: LearningWriteAdaptationEvaluationExecutionFeedbackExecutionRequest) -> Any:
        """Apply one exact prepared future execution request."""


class LearningWriteAdaptationEvaluationExecutionFeedbackExecutionService:
    """Execute one exact M22.41 preparation artifact through an applier."""

    def __init__(
        self,
        applier: LearningWriteAdaptationEvaluationExecutionFeedbackExecutionApplier,
    ) -> None:
        if not callable(getattr(applier, "apply", None)):
            raise TypeError("applier must provide an apply(request) method")
        self._applier = applier

    def execute(
        self,
        preparation: LearningWriteAdaptationEvaluationExecutionFeedbackPreparation,
    ) -> LearningWriteAdaptationEvaluationExecutionFeedbackExecutionResult:
        if not isinstance(
            preparation,
            LearningWriteAdaptationEvaluationExecutionFeedbackPreparation,
        ):
            raise TypeError(
                "preparation must be a LearningWriteAdaptationEvaluationExecutionFeedbackPreparation"
            )
        if (
            preparation.execution_authorized
            or preparation.execution_started
            or preparation.retry_requested
            or preparation.revocation_requested
            or preparation.memory_mutation_allowed
            or preparation.authority_granted
        ):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackExecutionError(
                "preparation cannot carry authorization, start state, retry, revocation, mutation, or authority"
            )

        execution_id = self._execution_id(preparation)
        request = LearningWriteAdaptationEvaluationExecutionFeedbackExecutionRequest(
            execution_id=execution_id,
            preparation_id=preparation.preparation_id,
            admission_id=preparation.admission_id,
            proposal_id=preparation.proposal_id,
            decision_id=preparation.decision_id,
            evaluation_id=preparation.evaluation_id,
            decision_source_evaluation_id=preparation.decision_source_evaluation_id,
            feedback_id=preparation.feedback_id,
            source_feedback_id=preparation.source_feedback_id,
            candidate_id=preparation.candidate_id,
            source_candidate_id=preparation.source_candidate_id,
            execution_source_id=preparation.execution_id,
            source_execution_id=preparation.source_execution_id,
            source_admission_id=preparation.source_admission_id,
            proposal_source_id=preparation.proposal_source_id,
            domain=preparation.domain,
            source_policy_id=preparation.source_policy_id,
            policy_id=preparation.policy_id,
            payload=preparation.payload,
            evidence=preparation.evidence,
            provenance=preparation.provenance,
        )
        try:
            result = self._applier.apply(request)
        except Exception as exc:  # noqa: BLE001
            return self._failed_result(preparation, execution_id, str(exc) or exc.__class__.__name__)
        return LearningWriteAdaptationEvaluationExecutionFeedbackExecutionResult(
            execution_id=execution_id,
            preparation_id=preparation.preparation_id,
            admission_id=preparation.admission_id,
            proposal_id=preparation.proposal_id,
            decision_id=preparation.decision_id,
            evaluation_id=preparation.evaluation_id,
            decision_source_evaluation_id=preparation.decision_source_evaluation_id,
            feedback_id=preparation.feedback_id,
            source_feedback_id=preparation.source_feedback_id,
            candidate_id=preparation.candidate_id,
            source_candidate_id=preparation.source_candidate_id,
            execution_source_id=preparation.execution_id,
            source_execution_id=preparation.source_execution_id,
            source_admission_id=preparation.source_admission_id,
            proposal_source_id=preparation.proposal_source_id,
            domain=preparation.domain,
            source_policy_id=preparation.source_policy_id,
            policy_id=preparation.policy_id,
            status=LearningWriteAdaptationEvaluationExecutionFeedbackExecutionStatus.COMPLETED,
            execution_result=result,
        )

    @staticmethod
    def _failed_result(
        preparation: LearningWriteAdaptationEvaluationExecutionFeedbackPreparation,
        execution_id: str,
        reason: str,
    ) -> LearningWriteAdaptationEvaluationExecutionFeedbackExecutionResult:
        return LearningWriteAdaptationEvaluationExecutionFeedbackExecutionResult(
            execution_id=execution_id,
            preparation_id=preparation.preparation_id,
            admission_id=preparation.admission_id,
            proposal_id=preparation.proposal_id,
            decision_id=preparation.decision_id,
            evaluation_id=preparation.evaluation_id,
            decision_source_evaluation_id=preparation.decision_source_evaluation_id,
            feedback_id=preparation.feedback_id,
            source_feedback_id=preparation.source_feedback_id,
            candidate_id=preparation.candidate_id,
            source_candidate_id=preparation.source_candidate_id,
            execution_source_id=preparation.execution_id,
            source_execution_id=preparation.source_execution_id,
            source_admission_id=preparation.source_admission_id,
            proposal_source_id=preparation.proposal_source_id,
            domain=preparation.domain,
            source_policy_id=preparation.source_policy_id,
            policy_id=preparation.policy_id,
            status=LearningWriteAdaptationEvaluationExecutionFeedbackExecutionStatus.FAILED,
            reason=reason,
        )

    @staticmethod
    def _execution_id(
        preparation: LearningWriteAdaptationEvaluationExecutionFeedbackPreparation,
    ) -> str:
        raw = json.dumps(
            {
                "preparation_id": preparation.preparation_id,
                "admission_id": preparation.admission_id,
                "proposal_id": preparation.proposal_id,
                "decision_id": preparation.decision_id,
                "evaluation_id": preparation.evaluation_id,
                "decision_source_evaluation_id": preparation.decision_source_evaluation_id,
                "feedback_id": preparation.feedback_id,
                "source_feedback_id": preparation.source_feedback_id,
                "candidate_id": preparation.candidate_id,
                "source_candidate_id": preparation.source_candidate_id,
                "execution_id": preparation.execution_id,
                "source_execution_id": preparation.source_execution_id,
                "source_admission_id": preparation.source_admission_id,
                "proposal_source_id": preparation.proposal_source_id,
                "domain": preparation.domain,
                "source_policy_id": preparation.source_policy_id,
                "policy_id": preparation.policy_id,
                "payload": dict(preparation.payload),
                "evidence": dict(preparation.evidence),
                "provenance": dict(preparation.provenance),
            },
            sort_keys=True,
            default=repr,
            separators=(",", ":"),
        ).encode("utf-8")
        return (
            "adaptation-evaluation-execution-feedback-execution-"
            f"{hashlib.sha256(raw).hexdigest()[:24]}"
        )
