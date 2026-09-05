"""Decision boundary after future adaptation execution-feedback evaluation.

This module turns immutable M22.37 evaluation evidence into an explicit,
immutable decision. The decision is advisory/non-authorizing and cannot
execute, retry, revoke, or mutate memory.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping, Protocol

from .learning_write_adaptation_evaluation_execution_feedback_evaluation import (
    LearningWriteAdaptationEvaluationExecutionFeedbackEvaluation,
    LearningWriteAdaptationEvaluationExecutionFeedbackSignalKind,
)


class LearningWriteAdaptationEvaluationExecutionFeedbackDecisionError(ValueError):
    """Raised when the M22.38 decision contract is invalid."""


class LearningWriteAdaptationEvaluationExecutionFeedbackAction(str, Enum):
    """Explicit decision for one future-execution feedback evaluation."""

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
class LearningWriteAdaptationEvaluationExecutionFeedbackDecisionContext:
    """Immutable context supplied to a M22.38 decision provider."""

    evaluation: LearningWriteAdaptationEvaluationExecutionFeedbackEvaluation
    related_context: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(
            self.evaluation,
            LearningWriteAdaptationEvaluationExecutionFeedbackEvaluation,
        ):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackDecisionError(
                "evaluation must be a LearningWriteAdaptationEvaluationExecutionFeedbackEvaluation"
            )
        if not isinstance(self.related_context, Mapping):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackDecisionError(
                "related_context must be a mapping"
            )
        object.__setattr__(self, "related_context", _freeze(self.related_context))


@dataclass(frozen=True)
class LearningWriteAdaptationEvaluationExecutionFeedbackDecision:
    """Immutable decision derived from M22.37 evaluation evidence."""

    decision_id: str
    evaluation_id: str
    feedback_id: str
    preparation_id: str
    admission_id: str
    proposal_id: str
    decision_source_evaluation_id: str
    source_feedback_id: str
    candidate_id: str
    source_candidate_id: str
    execution_id: str
    source_execution_id: str
    domain: str
    policy_id: str
    action: LearningWriteAdaptationEvaluationExecutionFeedbackAction
    reason: str
    confidence: float
    metadata: Mapping[str, Any] = field(default_factory=dict)
    execution_authorized: bool = False
    retry_requested: bool = False
    revocation_requested: bool = False
    memory_mutation_allowed: bool = False
    authority_granted: bool = False

    def __post_init__(self) -> None:
        for field_name, value in (
            ("decision_id", self.decision_id),
            ("evaluation_id", self.evaluation_id),
            ("feedback_id", self.feedback_id),
            ("preparation_id", self.preparation_id),
            ("admission_id", self.admission_id),
            ("proposal_id", self.proposal_id),
            ("decision_source_evaluation_id", self.decision_source_evaluation_id),
            ("source_feedback_id", self.source_feedback_id),
            ("candidate_id", self.candidate_id),
            ("source_candidate_id", self.source_candidate_id),
            ("execution_id", self.execution_id),
            ("source_execution_id", self.source_execution_id),
            ("domain", self.domain),
            ("policy_id", self.policy_id),
            ("reason", self.reason),
        ):
            if not isinstance(value, str) or not value.strip():
                raise LearningWriteAdaptationEvaluationExecutionFeedbackDecisionError(
                    f"{field_name} must be a non-empty string"
                )
        if not isinstance(
            self.action,
            LearningWriteAdaptationEvaluationExecutionFeedbackAction,
        ):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackDecisionError(
                "action must be a LearningWriteAdaptationEvaluationExecutionFeedbackAction member"
            )
        if not isinstance(self.confidence, (int, float)) or isinstance(self.confidence, bool):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackDecisionError(
                "confidence must be numeric"
            )
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise LearningWriteAdaptationEvaluationExecutionFeedbackDecisionError(
                "confidence must be between 0.0 and 1.0"
            )
        if not isinstance(self.metadata, Mapping):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackDecisionError(
                "metadata must be a mapping"
            )
        if self.execution_authorized or self.retry_requested or self.revocation_requested:
            raise LearningWriteAdaptationEvaluationExecutionFeedbackDecisionError(
                "feedback evaluation decision cannot authorize, retry, or revoke execution"
            )
        if self.memory_mutation_allowed or self.authority_granted:
            raise LearningWriteAdaptationEvaluationExecutionFeedbackDecisionError(
                "feedback evaluation decision cannot grant memory mutation or authority"
            )
        object.__setattr__(self, "metadata", _freeze(self.metadata))

    def to_context(self) -> dict[str, object]:
        return {
            "learning_write_adaptation_evaluation_execution_feedback_decision_id": self.decision_id,
            "learning_write_adaptation_evaluation_execution_feedback_evaluation_id": self.evaluation_id,
            "learning_write_adaptation_evaluation_execution_feedback_id": self.feedback_id,
            "learning_write_adaptation_evaluation_execution_preparation_id": self.preparation_id,
            "learning_write_adaptation_evaluation_proposal_admission_id": self.admission_id,
            "learning_write_adaptation_evaluation_proposal_id": self.proposal_id,
            "learning_write_adaptation_feedback_evaluation_id": self.decision_source_evaluation_id,
            "learning_write_adaptation_source_feedback_id": self.source_feedback_id,
            "learning_write_adaptation_candidate_id": self.candidate_id,
            "learning_candidate_id": self.source_candidate_id,
            "learning_write_adaptation_evaluation_execution_id": self.execution_id,
            "learning_write_adaptation_source_execution_id": self.source_execution_id,
            "learning_write_adaptation_domain": self.domain,
            "learning_write_adaptation_evaluation_execution_policy_id": self.policy_id,
            "adaptation_evaluation_execution_feedback_action": self.action.value,
            "reason": self.reason,
            "confidence": float(self.confidence),
            "metadata": dict(self.metadata),
            "execution_authorized": False,
            "authorization_granted": False,
            "retry_requested": False,
            "revocation_requested": False,
            "memory_mutation_allowed": False,
            "authority_granted": False,
        }


class LearningWriteAdaptationEvaluationExecutionFeedbackDecisionProvider(Protocol):
    """Provider-neutral, non-mutating M22.38 decision interface."""

    def decide(
        self,
        context: LearningWriteAdaptationEvaluationExecutionFeedbackDecisionContext,
    ) -> LearningWriteAdaptationEvaluationExecutionFeedbackDecision:
        ...


class DeterministicLearningWriteAdaptationEvaluationExecutionFeedbackDecisionProvider:
    """Deterministic baseline decision provider for M22.38."""

    def decide(
        self,
        context: LearningWriteAdaptationEvaluationExecutionFeedbackDecisionContext,
    ) -> LearningWriteAdaptationEvaluationExecutionFeedbackDecision:
        evaluation = context.evaluation
        if evaluation.signal is LearningWriteAdaptationEvaluationExecutionFeedbackSignalKind.EXECUTION_FAILURE_SIGNAL:
            action = LearningWriteAdaptationEvaluationExecutionFeedbackAction.DEFER
            reason = "failed future adaptation execution feedback requires further evidence before a downstream decision"
        elif evaluation.confidence < 0.5:
            action = LearningWriteAdaptationEvaluationExecutionFeedbackAction.DEFER
            reason = "future adaptation execution feedback evaluation confidence is below the deterministic acceptance threshold"
        else:
            action = LearningWriteAdaptationEvaluationExecutionFeedbackAction.ACCEPT
            reason = "future adaptation execution feedback evaluation provides sufficient observed evidence for the next boundary"

        decision_id = self._decision_id(evaluation, action)
        return LearningWriteAdaptationEvaluationExecutionFeedbackDecision(
            decision_id=decision_id,
            evaluation_id=evaluation.evaluation_id,
            feedback_id=evaluation.feedback_id,
            preparation_id=evaluation.preparation_id,
            admission_id=evaluation.admission_id,
            proposal_id=evaluation.proposal_id,
            decision_source_evaluation_id=evaluation.evaluation_id_from_feedback,
            source_feedback_id=evaluation.source_feedback_id,
            candidate_id=evaluation.candidate_id,
            source_candidate_id=evaluation.source_candidate_id,
            execution_id=evaluation.execution_id,
            source_execution_id=evaluation.source_execution_id,
            domain=evaluation.domain,
            policy_id=evaluation.policy_id,
            action=action,
            reason=reason,
            confidence=min(1.0, max(0.0, float(evaluation.confidence))),
            metadata={"provider": "deterministic"},
        )

    @staticmethod
    def _decision_id(
        evaluation: LearningWriteAdaptationEvaluationExecutionFeedbackEvaluation,
        action: LearningWriteAdaptationEvaluationExecutionFeedbackAction,
    ) -> str:
        payload = json.dumps(
            {
                "evaluation_id": evaluation.evaluation_id,
                "feedback_id": evaluation.feedback_id,
                "execution_id": evaluation.execution_id,
                "action": action.value,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return f"adaptation-evaluation-execution-feedback-decision-{hashlib.sha256(payload).hexdigest()[:24]}"


class LearningWriteAdaptationEvaluationExecutionFeedbackDecisionService:
    """Validate and obtain a non-authorizing M22.38 decision."""

    def __init__(
        self,
        provider: LearningWriteAdaptationEvaluationExecutionFeedbackDecisionProvider | None = None,
    ) -> None:
        self._provider = provider or DeterministicLearningWriteAdaptationEvaluationExecutionFeedbackDecisionProvider()

    def decide(
        self,
        context: LearningWriteAdaptationEvaluationExecutionFeedbackDecisionContext,
    ) -> LearningWriteAdaptationEvaluationExecutionFeedbackDecision:
        if not isinstance(
            context,
            LearningWriteAdaptationEvaluationExecutionFeedbackDecisionContext,
        ):
            raise TypeError(
                "context must be a LearningWriteAdaptationEvaluationExecutionFeedbackDecisionContext"
            )
        decision = self._provider.decide(context)
        if not isinstance(
            decision,
            LearningWriteAdaptationEvaluationExecutionFeedbackDecision,
        ):
            raise TypeError(
                "provider must return a LearningWriteAdaptationEvaluationExecutionFeedbackDecision"
            )
        evaluation = context.evaluation
        expected = (
            ("evaluation", decision.evaluation_id, evaluation.evaluation_id),
            ("feedback", decision.feedback_id, evaluation.feedback_id),
            ("preparation", decision.preparation_id, evaluation.preparation_id),
            ("admission", decision.admission_id, evaluation.admission_id),
            ("proposal", decision.proposal_id, evaluation.proposal_id),
            ("source feedback", decision.source_feedback_id, evaluation.source_feedback_id),
            ("candidate", decision.candidate_id, evaluation.candidate_id),
            ("source candidate", decision.source_candidate_id, evaluation.source_candidate_id),
            ("execution", decision.execution_id, evaluation.execution_id),
            ("source execution", decision.source_execution_id, evaluation.source_execution_id),
            ("domain", decision.domain, evaluation.domain),
            ("policy", decision.policy_id, evaluation.policy_id),
        )
        for label, actual, expected_value in expected:
            if actual != expected_value:
                raise LearningWriteAdaptationEvaluationExecutionFeedbackDecisionError(
                    f"decision {label} identity mismatch"
                )
        return decision
