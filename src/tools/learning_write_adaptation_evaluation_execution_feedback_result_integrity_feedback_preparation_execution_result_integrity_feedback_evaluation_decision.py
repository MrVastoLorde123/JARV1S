"""Decision boundary after the dedicated M22.53 evaluation artifact.

M22.54 converts exactly one M22.53 evaluation artifact into an explicit,
immutable advisory decision. The historical M22.46 decision namespace remains
untouched. The decision does not authorize execution, retry, revocation,
memory mutation, or adaptation truth.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping, Protocol

from .learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_preparation_execution_result_integrity_feedback_evaluation import (
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluation,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationSignalKind,
)


class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionError(ValueError):
    """Raised when the dedicated M22.54 decision contract is invalid."""


class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionAction(str, Enum):
    """Explicit advisory decision for one exact M22.53 evaluation."""

    ACCEPT = "accept"
    DEFER = "defer"
    REJECT = "reject"


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
class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionContext:
    """Immutable context supplied to an M22.54 decision provider."""

    evaluation: LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluation
    related_context: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(
            self.evaluation,
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluation,
        ):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionError(
                "evaluation must be a LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluation"
            )
        if not isinstance(self.related_context, Mapping):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionError(
                "related_context must be a mapping"
            )
        object.__setattr__(self, "related_context", _freeze(self.related_context))


@dataclass(frozen=True)
class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecision:
    """Immutable advisory decision derived from one exact M22.53 evaluation."""

    decision_id: str
    evaluation_id: str
    feedback_id: str
    integrity_id: str
    execution_id: str
    preparation_id: str
    admission_id: str
    proposal_id: str
    evaluation_id_from_feedback: str
    decision_source_evaluation_id: str
    source_feedback_id: str
    candidate_id: str
    source_candidate_id: str
    execution_source_id: str
    source_execution_id: str
    source_admission_id: str
    source_proposal_id: str
    domain: str
    source_policy_id: str
    policy_id: str
    action: LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionAction
    reason: str
    confidence: float
    metadata: Mapping[str, Any] = field(default_factory=dict)
    execution_authorized: bool = False
    retry_requested: bool = False
    revocation_requested: bool = False
    memory_mutation_allowed: bool = False
    authority_granted: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "decision_id", "evaluation_id", "feedback_id", "integrity_id", "execution_id",
            "preparation_id", "admission_id", "proposal_id", "evaluation_id_from_feedback",
            "decision_source_evaluation_id", "source_feedback_id", "candidate_id",
            "source_candidate_id", "execution_source_id", "source_execution_id",
            "source_admission_id", "source_proposal_id", "domain", "source_policy_id",
            "policy_id", "reason",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionError(
                    f"{field_name} must be a non-empty string"
                )
        if not isinstance(
            self.action,
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionAction,
        ):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionError(
                "action must be a LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionAction member"
            )
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionError(
                "confidence must be numeric"
            )
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionError(
                "confidence must be between 0.0 and 1.0"
            )
        if not isinstance(self.metadata, Mapping):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionError(
                "metadata must be a mapping"
            )
        if self.execution_authorized or self.retry_requested or self.revocation_requested:
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionError(
                "adaptation evaluation decision cannot authorize, retry, or revoke execution"
            )
        if self.memory_mutation_allowed or self.authority_granted:
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionError(
                "adaptation evaluation decision cannot grant memory mutation or authority"
            )
        object.__setattr__(self, "metadata", _freeze(self.metadata))

    def to_context(self) -> dict[str, object]:
        return {
            "learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_decision_id": self.decision_id,
            "learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_id": self.evaluation_id,
            "learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_id": self.feedback_id,
            "learning_write_adaptation_evaluation_execution_result_integrity_id": self.integrity_id,
            "learning_write_adaptation_evaluation_execution_id": self.execution_id,
            "learning_write_adaptation_evaluation_execution_preparation_id": self.preparation_id,
            "learning_write_adaptation_evaluation_execution_feedback_proposal_admission_id": self.admission_id,
            "learning_write_adaptation_evaluation_execution_feedback_proposal_id": self.proposal_id,
            "learning_write_adaptation_evaluation_feedback_evaluation_id_from_feedback": self.evaluation_id_from_feedback,
            "learning_write_adaptation_evaluation_feedback_decision_source_evaluation_id": self.decision_source_evaluation_id,
            "learning_write_adaptation_evaluation_execution_feedback_source_feedback_id": self.source_feedback_id,
            "learning_write_adaptation_candidate_id": self.candidate_id,
            "learning_candidate_id": self.source_candidate_id,
            "learning_write_adaptation_evaluation_execution_source_id": self.execution_source_id,
            "learning_write_adaptation_source_execution_id": self.source_execution_id,
            "learning_write_adaptation_evaluation_execution_source_admission_id": self.source_admission_id,
            "learning_write_adaptation_evaluation_proposal_id": self.source_proposal_id,
            "learning_write_adaptation_domain": self.domain,
            "learning_write_adaptation_source_policy_id": self.source_policy_id,
            "learning_write_adaptation_evaluation_execution_policy_id": self.policy_id,
            "adaptation_evaluation_decision_action": self.action.value,
            "reason": self.reason,
            "confidence": float(self.confidence),
            "metadata": dict(self.metadata),
            "execution_authorized": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
            "memory_mutation_allowed": False,
            "adaptation_truth_proven": False,
            "authority_granted": False,
        }


class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProvider(Protocol):
    """Provider-neutral, non-mutating M22.54 decision interface."""

    def decide(
        self,
        context: LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionContext,
    ) -> LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecision:
        ...


class DeterministicLearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProvider:
    """Deterministic baseline provider for M22.54."""

    def decide(
        self,
        context: LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionContext,
    ) -> LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecision:
        evaluation = context.evaluation
        if evaluation.signal is LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationSignalKind.INTEGRITY_FAILURE_SIGNAL:
            action = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionAction.DEFER
            reason = "integrity failure evaluation requires further evidence before a downstream decision"
        elif evaluation.confidence < 0.5:
            action = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionAction.DEFER
            reason = "evaluation confidence is below the deterministic acceptance threshold"
        else:
            action = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionAction.ACCEPT
            reason = "evaluation provides sufficient observed evidence for the next boundary"

        decision_id = self._decision_id(evaluation, action)
        return LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecision(
            decision_id=decision_id,
            evaluation_id=evaluation.evaluation_id,
            feedback_id=evaluation.feedback_id,
            integrity_id=evaluation.integrity_id,
            execution_id=evaluation.execution_id,
            preparation_id=evaluation.preparation_id,
            admission_id=evaluation.admission_id,
            proposal_id=evaluation.proposal_id,
            evaluation_id_from_feedback=evaluation.evaluation_id_from_feedback,
            decision_source_evaluation_id=evaluation.evaluation_id,
            source_feedback_id=evaluation.source_feedback_id,
            candidate_id=evaluation.candidate_id,
            source_candidate_id=evaluation.source_candidate_id,
            execution_source_id=evaluation.execution_source_id,
            source_execution_id=evaluation.source_execution_id,
            source_admission_id=evaluation.source_admission_id,
            source_proposal_id=evaluation.source_proposal_id,
            domain=evaluation.domain,
            source_policy_id=evaluation.source_policy_id,
            policy_id=evaluation.policy_id,
            action=action,
            reason=reason,
            confidence=min(1.0, max(0.0, float(evaluation.confidence))),
            metadata={"provider": "deterministic", "evaluation_signal": evaluation.signal.value},
        )

    @staticmethod
    def _decision_id(
        evaluation: LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluation,
        action: LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionAction,
    ) -> str:
        payload = json.dumps(
            {
                "evaluation_id": evaluation.evaluation_id,
                "feedback_id": evaluation.feedback_id,
                "integrity_id": evaluation.integrity_id,
                "action": action.value,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return (
            "adaptation-evaluation-execution-feedback-result-integrity-feedback-evaluation-decision-"
            + hashlib.sha256(payload).hexdigest()[:24]
        )


class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionService:
    """Validate and obtain a non-authorizing M22.54 decision."""

    def __init__(
        self,
        provider: LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProvider | None = None,
    ) -> None:
        self._provider = provider or DeterministicLearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProvider()

    def decide(
        self,
        context: LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionContext,
    ) -> LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecision:
        if not isinstance(
            context,
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionContext,
        ):
            raise TypeError(
                "context must be a LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionContext"
            )
        decision = self._provider.decide(context)
        if not isinstance(
            decision,
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecision,
        ):
            raise TypeError(
                "provider must return a LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecision"
            )
        evaluation = context.evaluation
        expected = (
            ("evaluation", decision.evaluation_id, evaluation.evaluation_id),
            ("feedback", decision.feedback_id, evaluation.feedback_id),
            ("integrity", decision.integrity_id, evaluation.integrity_id),
            ("execution", decision.execution_id, evaluation.execution_id),
            ("preparation", decision.preparation_id, evaluation.preparation_id),
            ("admission", decision.admission_id, evaluation.admission_id),
            ("proposal", decision.proposal_id, evaluation.proposal_id),
            ("evaluation from feedback", decision.evaluation_id_from_feedback, evaluation.evaluation_id_from_feedback),
            ("source feedback", decision.source_feedback_id, evaluation.source_feedback_id),
            ("candidate", decision.candidate_id, evaluation.candidate_id),
            ("source candidate", decision.source_candidate_id, evaluation.source_candidate_id),
            ("execution source", decision.execution_source_id, evaluation.execution_source_id),
            ("source execution", decision.source_execution_id, evaluation.source_execution_id),
            ("source admission", decision.source_admission_id, evaluation.source_admission_id),
            ("source proposal", decision.source_proposal_id, evaluation.source_proposal_id),
            ("domain", decision.domain, evaluation.domain),
            ("source policy", decision.source_policy_id, evaluation.source_policy_id),
            ("policy", decision.policy_id, evaluation.policy_id),
        )
        for label, actual, expected_value in expected:
            if actual != expected_value:
                raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionError(
                    f"decision {label} identity mismatch"
                )
        if decision.decision_source_evaluation_id != evaluation.evaluation_id:
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionError(
                "decision source evaluation identity mismatch"
            )
        return decision
