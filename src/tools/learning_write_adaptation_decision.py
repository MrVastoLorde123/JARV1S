"""Decision boundary after learning-write adaptation evaluation.

This module turns an inert adaptation candidate into an immutable decision.
It does not write learning or memory, authorize execution, retry, revoke, or
execute tools.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping, Protocol

from .learning_write_feedback_evaluation import LearningWriteAdaptationCandidate


class LearningWriteAdaptationDecisionError(ValueError):
    """Raised when the adaptation-decision contract is invalid."""


class LearningWriteAdaptationAction(str, Enum):
    """Explicit decision for an adaptation candidate."""

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
class LearningWriteAdaptationDecisionContext:
    """Immutable context supplied to an adaptation decision provider."""

    candidate: LearningWriteAdaptationCandidate
    related_context: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.candidate, LearningWriteAdaptationCandidate):
            raise LearningWriteAdaptationDecisionError(
                "candidate must be a LearningWriteAdaptationCandidate"
            )
        if not isinstance(self.related_context, Mapping):
            raise LearningWriteAdaptationDecisionError("related_context must be a mapping")
        object.__setattr__(self, "related_context", _freeze(self.related_context))


@dataclass(frozen=True)
class LearningWriteAdaptationDecision:
    """Immutable, non-authorizing adaptation decision."""

    decision_id: str
    candidate_id: str
    feedback_id: str
    execution_id: str
    admission_id: str
    proposal_id: str
    source_candidate_id: str
    domain: str
    action: LearningWriteAdaptationAction
    reason: str
    confidence: float
    metadata: Mapping[str, Any] = field(default_factory=dict)
    adaptation_write_allowed: bool = False
    memory_mutation_allowed: bool = False
    authority_granted: bool = False

    def __post_init__(self) -> None:
        for field_name, value in (
            ("decision_id", self.decision_id),
            ("candidate_id", self.candidate_id),
            ("feedback_id", self.feedback_id),
            ("execution_id", self.execution_id),
            ("admission_id", self.admission_id),
            ("proposal_id", self.proposal_id),
            ("source_candidate_id", self.source_candidate_id),
            ("domain", self.domain),
            ("reason", self.reason),
        ):
            if not isinstance(value, str) or not value.strip():
                raise LearningWriteAdaptationDecisionError(
                    f"{field_name} must be a non-empty string"
                )
        if not isinstance(self.action, LearningWriteAdaptationAction):
            raise LearningWriteAdaptationDecisionError(
                "action must be a LearningWriteAdaptationAction member"
            )
        if not isinstance(self.confidence, (int, float)) or isinstance(self.confidence, bool):
            raise LearningWriteAdaptationDecisionError("confidence must be a number")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise LearningWriteAdaptationDecisionError(
                "confidence must be between 0.0 and 1.0"
            )
        if not isinstance(self.metadata, Mapping):
            raise LearningWriteAdaptationDecisionError("metadata must be a mapping")
        if self.adaptation_write_allowed or self.memory_mutation_allowed or self.authority_granted:
            raise LearningWriteAdaptationDecisionError(
                "adaptation decision cannot grant write, mutation, or authority"
            )
        object.__setattr__(self, "metadata", _freeze(self.metadata))

    def to_context(self) -> dict[str, object]:
        return {
            "learning_write_adaptation_decision_id": self.decision_id,
            "learning_write_adaptation_candidate_id": self.candidate_id,
            "learning_write_feedback_id": self.feedback_id,
            "learning_write_execution_id": self.execution_id,
            "learning_write_admission_id": self.admission_id,
            "learning_write_proposal_id": self.proposal_id,
            "learning_candidate_id": self.source_candidate_id,
            "learning_write_domain": self.domain,
            "adaptation_action": self.action.value,
            "reason": self.reason,
            "confidence": float(self.confidence),
            "metadata": dict(self.metadata),
            "adaptation_write_allowed": False,
            "memory_mutation_allowed": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
        }


class LearningWriteAdaptationDecisionProvider(Protocol):
    """Provider-neutral, non-mutating decision interface."""

    def decide(
        self, context: LearningWriteAdaptationDecisionContext
    ) -> LearningWriteAdaptationDecision:
        ...


class DeterministicLearningWriteAdaptationDecisionProvider:
    """Deterministic baseline provider for the adaptation decision boundary."""

    def decide(
        self, context: LearningWriteAdaptationDecisionContext
    ) -> LearningWriteAdaptationDecision:
        candidate = context.candidate
        if candidate.signal.value == "write_failure_signal":
            action = LearningWriteAdaptationAction.DEFER
            reason = "failed learning write requires further evaluation before adaptation"
        else:
            action = LearningWriteAdaptationAction.ACCEPT
            reason = "successful learning write provides sufficient observed evidence for adaptation review"

        decision_id = self._decision_id(candidate, action)
        return LearningWriteAdaptationDecision(
            decision_id=decision_id,
            candidate_id=candidate.candidate_id,
            feedback_id=candidate.feedback_id,
            execution_id=candidate.execution_id,
            admission_id=candidate.admission_id,
            proposal_id=candidate.proposal_id,
            source_candidate_id=candidate.source_candidate_id,
            domain=candidate.domain,
            action=action,
            reason=reason,
            confidence=0.5,
            metadata={"provider": "deterministic"},
        )

    @staticmethod
    def _decision_id(
        candidate: LearningWriteAdaptationCandidate,
        action: LearningWriteAdaptationAction,
    ) -> str:
        payload = json.dumps(
            {
                "candidate_id": candidate.candidate_id,
                "feedback_id": candidate.feedback_id,
                "execution_id": candidate.execution_id,
                "action": action.value,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return f"learn-write-adaptation-decision-{hashlib.sha256(payload).hexdigest()[:24]}"


class LearningWriteAdaptationDecisionService:
    """Validate and obtain a non-authorizing adaptation decision."""

    def __init__(
        self,
        provider: LearningWriteAdaptationDecisionProvider | None = None,
    ) -> None:
        self._provider = provider or DeterministicLearningWriteAdaptationDecisionProvider()

    def decide(
        self,
        context: LearningWriteAdaptationDecisionContext,
    ) -> LearningWriteAdaptationDecision:
        if not isinstance(context, LearningWriteAdaptationDecisionContext):
            raise TypeError("context must be a LearningWriteAdaptationDecisionContext")

        decision = self._provider.decide(context)
        if not isinstance(decision, LearningWriteAdaptationDecision):
            raise TypeError("provider must return a LearningWriteAdaptationDecision")
        if decision.candidate_id != context.candidate.candidate_id:
            raise LearningWriteAdaptationDecisionError("decision candidate identity mismatch")
        if decision.feedback_id != context.candidate.feedback_id:
            raise LearningWriteAdaptationDecisionError("decision feedback identity mismatch")
        if decision.execution_id != context.candidate.execution_id:
            raise LearningWriteAdaptationDecisionError("decision execution identity mismatch")
        if decision.admission_id != context.candidate.admission_id:
            raise LearningWriteAdaptationDecisionError("decision admission identity mismatch")
        if decision.proposal_id != context.candidate.proposal_id:
            raise LearningWriteAdaptationDecisionError("decision proposal identity mismatch")
        if decision.source_candidate_id != context.candidate.source_candidate_id:
            raise LearningWriteAdaptationDecisionError("decision source candidate identity mismatch")
        if decision.domain != context.candidate.domain:
            raise LearningWriteAdaptationDecisionError("decision domain identity mismatch")
        return decision
