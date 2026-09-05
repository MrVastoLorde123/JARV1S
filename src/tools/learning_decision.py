"""Learning decision boundary between candidates and memory mutation.

This module turns an inert ``LearningCandidate`` into a provider-neutral
learning decision. It deliberately does not write memory, execute tools,
change authorization, retry, or revoke capabilities.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Optional

from .feedback_evaluation import LearningCandidate, LearningSignalKind


class LearningDecisionError(ValueError):
    """Raised when the learning-decision contract is invalid."""


class LearningAction(str, Enum):
    """Decision about whether and how a candidate may proceed later."""

    ACCEPT = "accept"
    DEFER = "defer"
    REJECT = "reject"


@dataclass(frozen=True)
class LearningDecisionContext:
    """Provider-neutral context for deciding what to do with a candidate."""

    candidate: LearningCandidate
    related_context: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class LearningDecision:
    """Immutable learning decision with no memory mutation authority."""

    decision_id: str
    candidate_id: str
    action: LearningAction
    reason: str
    confidence: float
    metadata: Mapping[str, Any] = ()  # normalized in __post_init__
    learning_write_allowed: bool = False
    authority_granted: bool = False

    def __post_init__(self) -> None:
        for field_name, value in (
            ("decision_id", self.decision_id),
            ("candidate_id", self.candidate_id),
            ("reason", self.reason),
        ):
            if not isinstance(value, str) or not value.strip():
                raise LearningDecisionError(f"{field_name} must be a non-empty string")
        if not isinstance(self.action, LearningAction):
            raise LearningDecisionError("action must be a LearningAction member")
        if not isinstance(self.confidence, (int, float)) or isinstance(self.confidence, bool):
            raise LearningDecisionError("confidence must be a number")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise LearningDecisionError("confidence must be between 0.0 and 1.0")
        if not isinstance(self.metadata, Mapping):
            raise LearningDecisionError("metadata must be a mapping")
        if self.learning_write_allowed:
            raise LearningDecisionError("learning decisions cannot grant learning-write authority")
        if self.authority_granted:
            raise LearningDecisionError("learning decisions cannot grant authority")

    def to_context(self) -> dict[str, object]:
        return {
            "learning_decision_id": self.decision_id,
            "learning_candidate_id": self.candidate_id,
            "learning_action": self.action.value,
            "learning_decision_reason": self.reason,
            "confidence": float(self.confidence),
            "metadata": dict(self.metadata),
            "learning_write_allowed": False,
            "learning_written": False,
            "memory_mutated": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
        }


class LearningDecisionProvider:
    """Provider-neutral contract for learning decisions."""

    def decide(self, context: LearningDecisionContext) -> LearningDecision:
        raise NotImplementedError

    def provider_name(self) -> str:
        raise NotImplementedError


class DeterministicLearningDecisionProvider(LearningDecisionProvider):
    """Dependency-free baseline provider for deterministic tests and fallback."""

    def provider_name(self) -> str:
        return "deterministic"

    def decide(self, context: LearningDecisionContext) -> LearningDecision:
        if not isinstance(context, LearningDecisionContext):
            raise TypeError("context must be a LearningDecisionContext")

        candidate = context.candidate
        if not isinstance(candidate, LearningCandidate):
            raise TypeError("context.candidate must be a LearningCandidate")

        if candidate.signal is LearningSignalKind.EXECUTOR_FAILURE_SIGNAL:
            action = LearningAction.DEFER
            reason = "executor failure should be evaluated after operational context is understood"
        elif candidate.signal is LearningSignalKind.TOOL_FAILURE_SIGNAL:
            action = LearningAction.ACCEPT
            reason = "tool failure is a learning-relevant signal that may proceed to a later learning write policy"
        else:
            action = LearningAction.ACCEPT
            reason = "successful execution is a learning-relevant signal that may proceed to a later learning write policy"

        decision_id = self._decision_id(candidate, action)
        return LearningDecision(
            decision_id=decision_id,
            candidate_id=candidate.candidate_id,
            action=action,
            reason=reason,
            confidence=min(float(candidate.confidence), 1.0),
            metadata={"provider": self.provider_name()},
        )

    @staticmethod
    def _decision_id(candidate: LearningCandidate, action: LearningAction) -> str:
        import hashlib
        import json

        payload = json.dumps(
            {
                "candidate_id": candidate.candidate_id,
                "action": action.value,
                "signal": candidate.signal.value,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return f"learn-decision-{hashlib.sha256(payload).hexdigest()[:24]}"


class LearningDecisionService:
    """Resolve learning candidates through a replaceable decision provider."""

    def __init__(self, provider: Optional[LearningDecisionProvider] = None) -> None:
        self._provider = provider or DeterministicLearningDecisionProvider()
        if not isinstance(self._provider, LearningDecisionProvider):
            raise TypeError("provider must implement LearningDecisionProvider")

    def decide(self, context: LearningDecisionContext) -> LearningDecision:
        if not isinstance(context, LearningDecisionContext):
            raise TypeError("context must be a LearningDecisionContext")
        decision = self._provider.decide(context)
        if not isinstance(decision, LearningDecision):
            raise TypeError("learning decision provider must return LearningDecision")
        if decision.candidate_id != context.candidate.candidate_id:
            raise LearningDecisionError("decision candidate identity does not match context")
        return decision
