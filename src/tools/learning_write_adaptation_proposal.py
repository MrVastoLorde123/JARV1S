"""Inert adaptation proposal boundary after an adaptation decision.

This module converts an accepted adaptation decision plus its exact source
candidate into a structured proposal for later adaptation policy/admission.
It does not mutate learning or memory, authorize execution, retry, revoke, or
execute tools.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping

from .learning_write_adaptation_decision import (
    LearningWriteAdaptationAction,
    LearningWriteAdaptationDecision,
    LearningWriteAdaptationDecisionContext,
)
from .learning_write_feedback_evaluation import LearningWriteAdaptationCandidate


class LearningWriteAdaptationProposalError(ValueError):
    """Raised when the adaptation-proposal contract is invalid."""


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
class LearningWriteAdaptationProposalContext:
    """Exact inputs required to construct an inert adaptation proposal."""

    decision: LearningWriteAdaptationDecision
    candidate: LearningWriteAdaptationCandidate
    adaptation: Mapping[str, Any]

    def __post_init__(self) -> None:
        if not isinstance(self.decision, LearningWriteAdaptationDecision):
            raise LearningWriteAdaptationProposalError(
                "decision must be a LearningWriteAdaptationDecision"
            )
        if not isinstance(self.candidate, LearningWriteAdaptationCandidate):
            raise LearningWriteAdaptationProposalError(
                "candidate must be a LearningWriteAdaptationCandidate"
            )
        if not isinstance(self.adaptation, Mapping):
            raise LearningWriteAdaptationProposalError("adaptation must be a mapping")
        object.__setattr__(self, "adaptation", _freeze(self.adaptation))


@dataclass(frozen=True)
class LearningWriteAdaptationProposal:
    """Immutable adaptation proposal that carries no mutation or authority."""

    proposal_id: str
    decision_id: str
    candidate_id: str
    feedback_id: str
    execution_id: str
    admission_id: str
    proposal_source_candidate_id: str
    domain: str
    adaptation: Mapping[str, Any]
    evidence: Mapping[str, Any]
    provenance: Mapping[str, str]
    confidence: float
    reason: str
    adaptation_write_allowed: bool = False
    memory_mutation_allowed: bool = False
    authority_granted: bool = False

    def __post_init__(self) -> None:
        for field_name, value in (
            ("proposal_id", self.proposal_id),
            ("decision_id", self.decision_id),
            ("candidate_id", self.candidate_id),
            ("feedback_id", self.feedback_id),
            ("execution_id", self.execution_id),
            ("admission_id", self.admission_id),
            ("proposal_source_candidate_id", self.proposal_source_candidate_id),
            ("domain", self.domain),
            ("reason", self.reason),
        ):
            if not isinstance(value, str) or not value.strip():
                raise LearningWriteAdaptationProposalError(
                    f"{field_name} must be a non-empty string"
                )
        for field_name, value in (
            ("adaptation", self.adaptation),
            ("evidence", self.evidence),
            ("provenance", self.provenance),
        ):
            if not isinstance(value, Mapping):
                raise LearningWriteAdaptationProposalError(
                    f"{field_name} must be a mapping"
                )
        if not all(
            isinstance(key, str) and key.strip()
            and isinstance(value, str) and value.strip()
            for key, value in self.provenance.items()
        ):
            raise LearningWriteAdaptationProposalError(
                "provenance must contain non-empty string keys and values"
            )
        if not isinstance(self.confidence, (int, float)) or isinstance(self.confidence, bool):
            raise LearningWriteAdaptationProposalError("confidence must be a number")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise LearningWriteAdaptationProposalError(
                "confidence must be between 0.0 and 1.0"
            )
        if self.adaptation_write_allowed:
            raise LearningWriteAdaptationProposalError(
                "an adaptation proposal cannot grant adaptation-write authority"
            )
        if self.memory_mutation_allowed:
            raise LearningWriteAdaptationProposalError(
                "an adaptation proposal cannot grant memory-mutation authority"
            )
        if self.authority_granted:
            raise LearningWriteAdaptationProposalError(
                "an adaptation proposal cannot grant authority"
            )

        object.__setattr__(self, "adaptation", _freeze(self.adaptation))
        object.__setattr__(self, "evidence", _freeze(self.evidence))
        object.__setattr__(self, "provenance", _freeze(self.provenance))

    def to_context(self) -> dict[str, object]:
        return {
            "learning_write_adaptation_proposal_id": self.proposal_id,
            "learning_write_adaptation_decision_id": self.decision_id,
            "learning_write_adaptation_candidate_id": self.candidate_id,
            "learning_write_feedback_id": self.feedback_id,
            "learning_write_execution_id": self.execution_id,
            "learning_write_admission_id": self.admission_id,
            "learning_candidate_id": self.proposal_source_candidate_id,
            "learning_write_domain": self.domain,
            "adaptation": dict(self.adaptation),
            "evidence": dict(self.evidence),
            "provenance": dict(self.provenance),
            "confidence": float(self.confidence),
            "adaptation_write_allowed": False,
            "memory_mutation_allowed": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
        }


class LearningWriteAdaptationProposalService:
    """Create inert adaptation proposals from accepted adaptation decisions."""

    def propose(
        self, context: LearningWriteAdaptationProposalContext
    ) -> LearningWriteAdaptationProposal | None:
        if not isinstance(context, LearningWriteAdaptationProposalContext):
            raise TypeError("context must be a LearningWriteAdaptationProposalContext")

        decision = context.decision
        candidate = context.candidate
        if decision.candidate_id != candidate.candidate_id:
            raise LearningWriteAdaptationProposalError(
                "adaptation decision candidate identity does not match source candidate"
            )
        if decision.feedback_id != candidate.feedback_id:
            raise LearningWriteAdaptationProposalError(
                "adaptation decision feedback identity does not match source candidate"
            )
        if decision.execution_id != candidate.execution_id:
            raise LearningWriteAdaptationProposalError(
                "adaptation decision execution identity does not match source candidate"
            )
        if decision.admission_id != candidate.admission_id:
            raise LearningWriteAdaptationProposalError(
                "adaptation decision admission identity does not match source candidate"
            )
        if decision.proposal_id != candidate.proposal_id:
            raise LearningWriteAdaptationProposalError(
                "adaptation decision proposal identity does not match source candidate"
            )
        if decision.source_candidate_id != candidate.source_candidate_id:
            raise LearningWriteAdaptationProposalError(
                "adaptation decision source candidate identity does not match source candidate"
            )
        if decision.domain != candidate.domain:
            raise LearningWriteAdaptationProposalError(
                "adaptation decision domain identity does not match source candidate"
            )
        if decision.action is not LearningWriteAdaptationAction.ACCEPT:
            return None

        return LearningWriteAdaptationProposal(
            proposal_id=self._proposal_id(decision, candidate, context.adaptation),
            decision_id=decision.decision_id,
            candidate_id=candidate.candidate_id,
            feedback_id=candidate.feedback_id,
            execution_id=candidate.execution_id,
            admission_id=candidate.admission_id,
            proposal_source_candidate_id=candidate.source_candidate_id,
            domain=candidate.domain,
            adaptation=context.adaptation,
            evidence=candidate.evidence,
            provenance=candidate.provenance,
            confidence=min(float(decision.confidence), float(candidate.confidence)),
            reason="accepted adaptation decision may proceed to later adaptation policy and admission",
        )

    @staticmethod
    def _proposal_id(
        decision: LearningWriteAdaptationDecision,
        candidate: LearningWriteAdaptationCandidate,
        adaptation: Mapping[str, Any],
    ) -> str:
        serialized = json.dumps(
            {
                "decision_id": decision.decision_id,
                "candidate_id": candidate.candidate_id,
                "feedback_id": candidate.feedback_id,
                "execution_id": candidate.execution_id,
                "adaptation": adaptation,
            },
            sort_keys=True,
            default=repr,
            separators=(",", ":"),
        ).encode("utf-8")
        return f"learn-write-adaptation-proposal-{hashlib.sha256(serialized).hexdigest()[:24]}"
