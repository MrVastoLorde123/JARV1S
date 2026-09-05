"""Proposal boundary after adaptation-evaluation decision.

This module turns an accepted adaptation-evaluation decision into an immutable
proposal for a later admission boundary. It does not admit, execute,
authorize, retry, revoke, or mutate memory.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping

from .learning_write_adaptation_evaluation_decision import (
    LearningWriteAdaptationEvaluationAction,
    LearningWriteAdaptationEvaluationDecision,
)


class LearningWriteAdaptationEvaluationProposalError(ValueError):
    """Raised when the adaptation-evaluation proposal contract is invalid."""


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
class LearningWriteAdaptationEvaluationProposalContext:
    """Immutable context for constructing a downstream evaluation proposal."""

    decision: LearningWriteAdaptationEvaluationDecision
    proposal: Mapping[str, Any]

    def __post_init__(self) -> None:
        if not isinstance(self.decision, LearningWriteAdaptationEvaluationDecision):
            raise LearningWriteAdaptationEvaluationProposalError(
                "decision must be a LearningWriteAdaptationEvaluationDecision"
            )
        if not isinstance(self.proposal, Mapping):
            raise LearningWriteAdaptationEvaluationProposalError(
                "proposal must be a mapping"
            )
        if not self.proposal:
            raise LearningWriteAdaptationEvaluationProposalError(
                "proposal must not be empty"
            )
        object.__setattr__(self, "proposal", _freeze(self.proposal))


@dataclass(frozen=True)
class LearningWriteAdaptationEvaluationProposal:
    """Immutable, inert proposal derived from an accepted evaluation decision."""

    proposal_id: str
    decision_id: str
    evaluation_id: str
    feedback_id: str
    source_feedback_id: str
    candidate_id: str
    execution_id: str
    admission_id: str
    source_candidate_id: str
    domain: str
    proposal: Mapping[str, Any]
    evidence: Mapping[str, Any]
    provenance: Mapping[str, str]
    confidence: float
    reason: str
    adaptation_authorized: bool = False
    memory_mutation_allowed: bool = False
    execution_requested: bool = False

    def __post_init__(self) -> None:
        for field_name, value in (
            ("proposal_id", self.proposal_id),
            ("decision_id", self.decision_id),
            ("evaluation_id", self.evaluation_id),
            ("feedback_id", self.feedback_id),
            ("source_feedback_id", self.source_feedback_id),
            ("candidate_id", self.candidate_id),
            ("execution_id", self.execution_id),
            ("admission_id", self.admission_id),
            ("source_candidate_id", self.source_candidate_id),
            ("domain", self.domain),
            ("reason", self.reason),
        ):
            if not isinstance(value, str) or not value.strip():
                raise LearningWriteAdaptationEvaluationProposalError(
                    f"{field_name} must be a non-empty string"
                )
        if not isinstance(self.confidence, (int, float)) or isinstance(self.confidence, bool):
            raise LearningWriteAdaptationEvaluationProposalError(
                "confidence must be a number"
            )
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise LearningWriteAdaptationEvaluationProposalError(
                "confidence must be between 0.0 and 1.0"
            )
        for field_name, value in (("proposal", self.proposal), ("evidence", self.evidence)):
            if not isinstance(value, Mapping):
                raise LearningWriteAdaptationEvaluationProposalError(
                    f"{field_name} must be a mapping"
                )
        if not isinstance(self.provenance, Mapping):
            raise LearningWriteAdaptationEvaluationProposalError(
                "provenance must be a mapping"
            )
        if not all(
            isinstance(key, str)
            and key.strip()
            and isinstance(value, str)
            and value.strip()
            for key, value in self.provenance.items()
        ):
            raise LearningWriteAdaptationEvaluationProposalError(
                "provenance must contain non-empty string keys and values"
            )
        if self.adaptation_authorized or self.memory_mutation_allowed or self.execution_requested:
            raise LearningWriteAdaptationEvaluationProposalError(
                "proposal cannot grant authorization, mutation, or execution"
            )
        object.__setattr__(self, "proposal", _freeze(self.proposal))
        object.__setattr__(self, "evidence", _freeze(self.evidence))
        object.__setattr__(self, "provenance", _freeze(self.provenance))

    def to_context(self) -> dict[str, object]:
        return {
            "learning_write_adaptation_evaluation_proposal_id": self.proposal_id,
            "learning_write_adaptation_evaluation_decision_id": self.decision_id,
            "learning_write_adaptation_feedback_evaluation_id": self.evaluation_id,
            "learning_write_adaptation_feedback_id": self.feedback_id,
            "learning_write_adaptation_source_feedback_id": self.source_feedback_id,
            "learning_write_adaptation_candidate_id": self.candidate_id,
            "learning_write_adaptation_execution_id": self.execution_id,
            "learning_write_adaptation_admission_id": self.admission_id,
            "learning_candidate_id": self.source_candidate_id,
            "learning_write_adaptation_domain": self.domain,
            "proposal": dict(self.proposal),
            "evidence": dict(self.evidence),
            "provenance": dict(self.provenance),
            "confidence": float(self.confidence),
            "reason": self.reason,
            "adaptation_authorized": False,
            "memory_mutation_allowed": False,
            "execution_requested": False,
            "authorization_granted": False,
            "retry_requested": False,
            "revocation_requested": False,
        }


class LearningWriteAdaptationEvaluationProposalService:
    """Create an inert proposal only from an accepted evaluation decision."""

    def propose(
        self,
        context: LearningWriteAdaptationEvaluationProposalContext,
    ) -> LearningWriteAdaptationEvaluationProposal | None:
        if not isinstance(context, LearningWriteAdaptationEvaluationProposalContext):
            raise TypeError(
                "context must be a LearningWriteAdaptationEvaluationProposalContext"
            )

        decision = context.decision
        if decision.action is not LearningWriteAdaptationEvaluationAction.ACCEPT:
            return None

        proposal_payload = dict(context.proposal)
        evidence = {
            "decision_action": decision.action.value,
            "decision_reason": decision.reason,
            "decision_confidence": decision.confidence,
            "evaluation_id": decision.evaluation_id,
        }
        provenance = {
            "source": "adaptation_evaluation_decision",
            "decision_id": decision.decision_id,
            "evaluation_id": decision.evaluation_id,
            "feedback_id": decision.feedback_id,
            "source_feedback_id": decision.source_feedback_id,
            "candidate_id": decision.candidate_id,
            "source_candidate_id": decision.source_candidate_id,
            "execution_id": decision.execution_id,
            "admission_id": decision.admission_id,
            "proposal_id": decision.proposal_id,
        }
        proposal_id = self._proposal_id(decision, proposal_payload)
        return LearningWriteAdaptationEvaluationProposal(
            proposal_id=proposal_id,
            decision_id=decision.decision_id,
            evaluation_id=decision.evaluation_id,
            feedback_id=decision.feedback_id,
            source_feedback_id=decision.source_feedback_id,
            candidate_id=decision.candidate_id,
            execution_id=decision.execution_id,
            admission_id=decision.admission_id,
            source_candidate_id=decision.source_candidate_id,
            domain=decision.domain,
            proposal=proposal_payload,
            evidence=evidence,
            provenance=provenance,
            confidence=float(decision.confidence),
            reason="accepted adaptation evaluation creates a proposal for downstream admission",
        )

    @staticmethod
    def _proposal_id(
        decision: LearningWriteAdaptationEvaluationDecision,
        proposal: Mapping[str, Any],
    ) -> str:
        payload = json.dumps(
            {
                "decision_id": decision.decision_id,
                "evaluation_id": decision.evaluation_id,
                "feedback_id": decision.feedback_id,
                "source_feedback_id": decision.source_feedback_id,
                "execution_id": decision.execution_id,
                "proposal": proposal,
            },
            sort_keys=True,
            default=repr,
            separators=(",", ":"),
        ).encode("utf-8")
        return f"adaptation-evaluation-proposal-{hashlib.sha256(payload).hexdigest()[:24]}"
