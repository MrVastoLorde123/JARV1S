"""Inert learning-write proposal boundary after a learning decision.

This module converts an accepted ``LearningDecision`` plus its exact source
``LearningCandidate`` into a structured proposal for a later learning-write
policy. It does not persist state, mutate memory, authorize execution,
retry, revoke, or execute tools.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping

from .feedback_evaluation import LearningCandidate
from .learning_decision import LearningAction, LearningDecision


class LearningWriteProposalError(ValueError):
    """Raised when the learning-write proposal contract is invalid."""


class LearningWriteDomain(str, Enum):
    """Explicit destination family for a later learning-write policy."""

    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    PREFERENCE = "preference"
    FAILURE_OUTCOME = "failure_outcome"
    BELIEF = "belief"
    PREDICTIVE = "predictive"
    META = "meta"


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
class LearningWriteProposalContext:
    """Exact inputs required to construct an inert write proposal."""

    decision: LearningDecision
    candidate: LearningCandidate
    domain: LearningWriteDomain
    payload: Mapping[str, Any]


@dataclass(frozen=True)
class LearningWriteProposal:
    """Immutable proposal that carries no mutation or authority."""

    proposal_id: str
    decision_id: str
    candidate_id: str
    feedback_id: str
    execution_id: str
    handoff_id: str
    tool_name: str
    domain: LearningWriteDomain
    payload: Mapping[str, Any]
    evidence: Mapping[str, Any]
    provenance: Mapping[str, str]
    confidence: float
    reason: str
    learning_write_allowed: bool = False
    authority_granted: bool = False
    memory_mutated: bool = False

    def __post_init__(self) -> None:
        for field_name, value in (
            ("proposal_id", self.proposal_id),
            ("decision_id", self.decision_id),
            ("candidate_id", self.candidate_id),
            ("feedback_id", self.feedback_id),
            ("execution_id", self.execution_id),
            ("handoff_id", self.handoff_id),
            ("tool_name", self.tool_name),
            ("reason", self.reason),
        ):
            if not isinstance(value, str) or not value.strip():
                raise LearningWriteProposalError(
                    f"{field_name} must be a non-empty string"
                )
        if not isinstance(self.domain, LearningWriteDomain):
            raise LearningWriteProposalError(
                "domain must be a LearningWriteDomain member"
            )
        for field_name, value in (
            ("payload", self.payload),
            ("evidence", self.evidence),
            ("provenance", self.provenance),
        ):
            if not isinstance(value, Mapping):
                raise LearningWriteProposalError(f"{field_name} must be a mapping")
        if not all(
            isinstance(key, str) and key.strip()
            and isinstance(value, str) and value.strip()
            for key, value in self.provenance.items()
        ):
            raise LearningWriteProposalError(
                "provenance must contain non-empty string keys and values"
            )
        if not isinstance(self.confidence, (int, float)) or isinstance(self.confidence, bool):
            raise LearningWriteProposalError("confidence must be a number")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise LearningWriteProposalError(
                "confidence must be between 0.0 and 1.0"
            )
        if self.learning_write_allowed:
            raise LearningWriteProposalError(
                "a proposal cannot grant learning-write authority"
            )
        if self.authority_granted:
            raise LearningWriteProposalError("a proposal cannot grant authority")
        if self.memory_mutated:
            raise LearningWriteProposalError(
                "a proposal cannot claim memory mutation"
            )

        object.__setattr__(self, "payload", _freeze(self.payload))
        object.__setattr__(self, "evidence", _freeze(self.evidence))
        object.__setattr__(self, "provenance", _freeze(self.provenance))

    def to_context(self) -> dict[str, object]:
        return {
            "learning_write_proposal_id": self.proposal_id,
            "learning_decision_id": self.decision_id,
            "learning_candidate_id": self.candidate_id,
            "feedback_id": self.feedback_id,
            "execution_id": self.execution_id,
            "handoff_id": self.handoff_id,
            "tool_name": self.tool_name,
            "learning_write_domain": self.domain.value,
            "payload": dict(self.payload),
            "evidence": dict(self.evidence),
            "provenance": dict(self.provenance),
            "confidence": float(self.confidence),
            "learning_write_allowed": False,
            "learning_written": False,
            "memory_mutated": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
        }


class LearningWriteProposalService:
    """Create inert write proposals from accepted learning decisions."""

    def propose(
        self,
        context: LearningWriteProposalContext,
    ) -> LearningWriteProposal | None:
        if not isinstance(context, LearningWriteProposalContext):
            raise TypeError("context must be a LearningWriteProposalContext")
        if not isinstance(context.decision, LearningDecision):
            raise TypeError("context.decision must be a LearningDecision")
        if not isinstance(context.candidate, LearningCandidate):
            raise TypeError("context.candidate must be a LearningCandidate")
        if not isinstance(context.domain, LearningWriteDomain):
            raise TypeError("context.domain must be a LearningWriteDomain")
        if not isinstance(context.payload, Mapping):
            raise TypeError("context.payload must be a mapping")

        decision = context.decision
        candidate = context.candidate

        if decision.candidate_id != candidate.candidate_id:
            raise LearningWriteProposalError(
                "learning decision candidate identity does not match source candidate"
            )
        if decision.action is not LearningAction.ACCEPT:
            return None

        return LearningWriteProposal(
            proposal_id=self._proposal_id(decision, context.domain, context.payload),
            decision_id=decision.decision_id,
            candidate_id=candidate.candidate_id,
            feedback_id=candidate.feedback_id,
            execution_id=candidate.execution_id,
            handoff_id=candidate.handoff_id,
            tool_name=candidate.tool_name,
            domain=context.domain,
            payload=context.payload,
            evidence=candidate.evidence,
            provenance=candidate.provenance,
            confidence=min(float(decision.confidence), float(candidate.confidence)),
            reason="accepted learning decision may proceed to a later learning-write policy",
        )

    @staticmethod
    def _proposal_id(
        decision: LearningDecision,
        domain: LearningWriteDomain,
        payload: Mapping[str, Any],
    ) -> str:
        serialized = json.dumps(
            {
                "decision_id": decision.decision_id,
                "candidate_id": decision.candidate_id,
                "domain": domain.value,
                "payload": payload,
            },
            sort_keys=True,
            default=repr,
            separators=(",", ":"),
        ).encode("utf-8")
        return f"learn-write-proposal-{hashlib.sha256(serialized).hexdigest()[:24]}"
