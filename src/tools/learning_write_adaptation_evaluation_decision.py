"""Decision boundary after adaptation-feedback evaluation.

This module turns an inert adaptation-feedback evaluation candidate into an
immutable decision. It does not authorize adaptation, mutate memory, retry,
revoke, or execute tools.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping, Protocol

from .learning_write_adaptation_feedback_evaluation import (
    LearningWriteAdaptationFeedbackEvaluationCandidate,
    LearningWriteAdaptationFeedbackSignalKind,
)


class LearningWriteAdaptationEvaluationDecisionError(ValueError):
    """Raised when the adaptation-evaluation decision contract is invalid."""


class LearningWriteAdaptationEvaluationAction(str, Enum):
    """Explicit decision for one adaptation-feedback evaluation."""

    ACCEPT = "accept"
    DEFER = "defer"
    REJECT = "reject"


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
class LearningWriteAdaptationEvaluationDecisionContext:
    """Immutable context supplied to an adaptation-evaluation decision provider."""

    evaluation: LearningWriteAdaptationFeedbackEvaluationCandidate
    related_context: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(
            self.evaluation, LearningWriteAdaptationFeedbackEvaluationCandidate
        ):
            raise LearningWriteAdaptationEvaluationDecisionError(
                "evaluation must be a LearningWriteAdaptationFeedbackEvaluationCandidate"
            )
        if not isinstance(self.related_context, Mapping):
            raise LearningWriteAdaptationEvaluationDecisionError(
                "related_context must be a mapping"
            )
        object.__setattr__(self, "related_context", _freeze(self.related_context))


@dataclass(frozen=True)
class LearningWriteAdaptationEvaluationDecision:
    """Immutable decision derived from adaptation-feedback evaluation evidence."""

    decision_id: str
    evaluation_id: str
    feedback_id: str
    source_feedback_id: str
    candidate_id: str
    execution_id: str
    admission_id: str
    proposal_id: str
    source_candidate_id: str
    domain: str
    action: LearningWriteAdaptationEvaluationAction
    reason: str
    confidence: float
    metadata: Mapping[str, Any] = field(default_factory=dict)
    adaptation_authorized: bool = False
    memory_mutation_allowed: bool = False
    authority_granted: bool = False

    def __post_init__(self) -> None:
        for field_name, value in (
            ("decision_id", self.decision_id),
            ("evaluation_id", self.evaluation_id),
            ("feedback_id", self.feedback_id),
            ("source_feedback_id", self.source_feedback_id),
            ("candidate_id", self.candidate_id),
            ("execution_id", self.execution_id),
            ("admission_id", self.admission_id),
            ("proposal_id", self.proposal_id),
            ("source_candidate_id", self.source_candidate_id),
            ("domain", self.domain),
            ("reason", self.reason),
        ):
            if not isinstance(value, str) or not value.strip():
                raise LearningWriteAdaptationEvaluationDecisionError(
                    f"{field_name} must be a non-empty string"
                )
        if not isinstance(self.action, LearningWriteAdaptationEvaluationAction):
            raise LearningWriteAdaptationEvaluationDecisionError(
                "action must be a LearningWriteAdaptationEvaluationAction member"
            )
        if not isinstance(self.confidence, (int, float)) or isinstance(self.confidence, bool):
            raise LearningWriteAdaptationEvaluationDecisionError(
                "confidence must be a number"
            )
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise LearningWriteAdaptationEvaluationDecisionError(
                "confidence must be between 0.0 and 1.0"
            )
        if not isinstance(self.metadata, Mapping):
            raise LearningWriteAdaptationEvaluationDecisionError(
                "metadata must be a mapping"
            )
        if self.adaptation_authorized or self.memory_mutation_allowed or self.authority_granted:
            raise LearningWriteAdaptationEvaluationDecisionError(
                "evaluation decision cannot grant adaptation, mutation, or authority"
            )
        object.__setattr__(self, "metadata", _freeze(self.metadata))

    def to_context(self) -> dict[str, object]:
        return {
            "learning_write_adaptation_evaluation_decision_id": self.decision_id,
            "learning_write_adaptation_feedback_evaluation_id": self.evaluation_id,
            "learning_write_adaptation_feedback_id": self.feedback_id,
            "learning_write_adaptation_source_feedback_id": self.source_feedback_id,
            "learning_write_adaptation_candidate_id": self.candidate_id,
            "learning_write_adaptation_execution_id": self.execution_id,
            "learning_write_adaptation_admission_id": self.admission_id,
            "learning_write_adaptation_proposal_id": self.proposal_id,
            "learning_candidate_id": self.source_candidate_id,
            "learning_write_adaptation_domain": self.domain,
            "adaptation_evaluation_action": self.action.value,
            "reason": self.reason,
            "confidence": float(self.confidence),
            "metadata": dict(self.metadata),
            "adaptation_authorized": False,
            "memory_mutation_allowed": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
        }


class LearningWriteAdaptationEvaluationDecisionProvider(Protocol):
    """Provider-neutral, non-mutating decision interface."""

    def decide(
        self,
        context: LearningWriteAdaptationEvaluationDecisionContext,
    ) -> LearningWriteAdaptationEvaluationDecision:
        ...


class DeterministicLearningWriteAdaptationEvaluationDecisionProvider:
    """Deterministic baseline provider for the evaluation-decision boundary."""

    def decide(
        self,
        context: LearningWriteAdaptationEvaluationDecisionContext,
    ) -> LearningWriteAdaptationEvaluationDecision:
        evaluation = context.evaluation
        if evaluation.signal is LearningWriteAdaptationFeedbackSignalKind.ADAPTATION_FAILURE_SIGNAL:
            action = LearningWriteAdaptationEvaluationAction.DEFER
            reason = "failed adaptation feedback requires further evidence before a decision"
        elif evaluation.confidence < 0.5:
            action = LearningWriteAdaptationEvaluationAction.DEFER
            reason = "adaptation evaluation confidence is below the deterministic acceptance threshold"
        else:
            action = LearningWriteAdaptationEvaluationAction.ACCEPT
            reason = "adaptation evaluation provides sufficient observed evidence for the next adaptation boundary"

        decision_id = self._decision_id(evaluation, action)
        return LearningWriteAdaptationEvaluationDecision(
            decision_id=decision_id,
            evaluation_id=evaluation.evaluation_id,
            feedback_id=evaluation.feedback_id,
            source_feedback_id=evaluation.source_feedback_id,
            candidate_id=evaluation.candidate_id,
            execution_id=evaluation.execution_id,
            admission_id=evaluation.admission_id,
            proposal_id=evaluation.proposal_id,
            source_candidate_id=evaluation.source_candidate_id,
            domain=evaluation.domain,
            action=action,
            reason=reason,
            confidence=min(1.0, max(0.0, float(evaluation.confidence))),
            metadata={"provider": "deterministic"},
        )

    @staticmethod
    def _decision_id(
        evaluation: LearningWriteAdaptationFeedbackEvaluationCandidate,
        action: LearningWriteAdaptationEvaluationAction,
    ) -> str:
        payload = json.dumps(
            {
                "evaluation_id": evaluation.evaluation_id,
                "feedback_id": evaluation.feedback_id,
                "source_feedback_id": evaluation.source_feedback_id,
                "execution_id": evaluation.execution_id,
                "action": action.value,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return f"adaptation-evaluation-decision-{hashlib.sha256(payload).hexdigest()[:24]}"


class LearningWriteAdaptationEvaluationDecisionService:
    """Validate and obtain a non-authorizing adaptation-evaluation decision."""

    def __init__(
        self,
        provider: LearningWriteAdaptationEvaluationDecisionProvider | None = None,
    ) -> None:
        self._provider = provider or DeterministicLearningWriteAdaptationEvaluationDecisionProvider()

    def decide(
        self,
        context: LearningWriteAdaptationEvaluationDecisionContext,
    ) -> LearningWriteAdaptationEvaluationDecision:
        if not isinstance(context, LearningWriteAdaptationEvaluationDecisionContext):
            raise TypeError(
                "context must be a LearningWriteAdaptationEvaluationDecisionContext"
            )

        decision = self._provider.decide(context)
        if not isinstance(decision, LearningWriteAdaptationEvaluationDecision):
            raise TypeError(
                "provider must return a LearningWriteAdaptationEvaluationDecision"
            )

        expected = (
            ("evaluation", decision.evaluation_id, context.evaluation.evaluation_id),
            ("feedback", decision.feedback_id, context.evaluation.feedback_id),
            ("source feedback", decision.source_feedback_id, context.evaluation.source_feedback_id),
            ("candidate", decision.candidate_id, context.evaluation.candidate_id),
            ("execution", decision.execution_id, context.evaluation.execution_id),
            ("admission", decision.admission_id, context.evaluation.admission_id),
            ("proposal", decision.proposal_id, context.evaluation.proposal_id),
            ("source candidate", decision.source_candidate_id, context.evaluation.source_candidate_id),
            ("domain", decision.domain, context.evaluation.domain),
        )
        for label, actual, expected_value in expected:
            if actual != expected_value:
                raise LearningWriteAdaptationEvaluationDecisionError(
                    f"decision {label} identity mismatch"
                )
        return decision
