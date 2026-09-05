"""Proposal boundary after future-adaptation execution feedback decision.

This module turns an accepted M22.38 decision into an immutable downstream
proposal. It does not admit, authorize, execute, retry, revoke, or mutate
memory.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping

from .learning_write_adaptation_evaluation_execution_feedback_decision import (
    LearningWriteAdaptationEvaluationExecutionFeedbackAction,
    LearningWriteAdaptationEvaluationExecutionFeedbackDecision,
)


class LearningWriteAdaptationEvaluationExecutionFeedbackProposalError(ValueError):
    """Raised when the M22.39 proposal contract is invalid."""


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
class LearningWriteAdaptationEvaluationExecutionFeedbackProposalContext:
    """Immutable context for constructing an execution-feedback proposal."""

    decision: LearningWriteAdaptationEvaluationExecutionFeedbackDecision
    proposal: Mapping[str, Any]

    def __post_init__(self) -> None:
        if not isinstance(
            self.decision,
            LearningWriteAdaptationEvaluationExecutionFeedbackDecision,
        ):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackProposalError(
                "decision must be a LearningWriteAdaptationEvaluationExecutionFeedbackDecision"
            )
        if not isinstance(self.proposal, Mapping):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackProposalError(
                "proposal must be a mapping"
            )
        if not self.proposal:
            raise LearningWriteAdaptationEvaluationExecutionFeedbackProposalError(
                "proposal must not be empty"
            )
        object.__setattr__(self, "proposal", _freeze(self.proposal))


@dataclass(frozen=True)
class LearningWriteAdaptationEvaluationExecutionFeedbackProposal:
    """Immutable, inert proposal derived from an accepted M22.38 decision."""

    proposal_id: str
    decision_id: str
    evaluation_id: str
    decision_source_evaluation_id: str
    feedback_id: str
    source_feedback_id: str
    candidate_id: str
    source_candidate_id: str
    execution_id: str
    source_execution_id: str
    preparation_id: str
    admission_id: str
    proposal_source_id: str
    domain: str
    policy_id: str
    proposal: Mapping[str, Any]
    evidence: Mapping[str, Any]
    provenance: Mapping[str, str]
    confidence: float
    reason: str
    adaptation_authorized: bool = False
    execution_requested: bool = False
    retry_requested: bool = False
    revocation_requested: bool = False
    memory_mutation_allowed: bool = False

    def __post_init__(self) -> None:
        for field_name, value in (
            ("proposal_id", self.proposal_id),
            ("decision_id", self.decision_id),
            ("evaluation_id", self.evaluation_id),
            ("decision_source_evaluation_id", self.decision_source_evaluation_id),
            ("feedback_id", self.feedback_id),
            ("source_feedback_id", self.source_feedback_id),
            ("candidate_id", self.candidate_id),
            ("source_candidate_id", self.source_candidate_id),
            ("execution_id", self.execution_id),
            ("source_execution_id", self.source_execution_id),
            ("preparation_id", self.preparation_id),
            ("admission_id", self.admission_id),
            ("proposal_source_id", self.proposal_source_id),
            ("domain", self.domain),
            ("policy_id", self.policy_id),
            ("reason", self.reason),
        ):
            if not isinstance(value, str) or not value.strip():
                raise LearningWriteAdaptationEvaluationExecutionFeedbackProposalError(
                    f"{field_name} must be a non-empty string"
                )
        if not isinstance(self.confidence, (int, float)) or isinstance(self.confidence, bool):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackProposalError(
                "confidence must be a number"
            )
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise LearningWriteAdaptationEvaluationExecutionFeedbackProposalError(
                "confidence must be between 0.0 and 1.0"
            )
        for field_name, value in (("proposal", self.proposal), ("evidence", self.evidence)):
            if not isinstance(value, Mapping):
                raise LearningWriteAdaptationEvaluationExecutionFeedbackProposalError(
                    f"{field_name} must be a mapping"
                )
        if not isinstance(self.provenance, Mapping):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackProposalError(
                "provenance must be a mapping"
            )
        if not all(
            isinstance(key, str)
            and key.strip()
            and isinstance(value, str)
            and value.strip()
            for key, value in self.provenance.items()
        ):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackProposalError(
                "provenance must contain non-empty string keys and values"
            )
        if (
            self.adaptation_authorized
            or self.execution_requested
            or self.retry_requested
            or self.revocation_requested
            or self.memory_mutation_allowed
        ):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackProposalError(
                "proposal cannot grant authorization, execution, retry, revocation, or memory mutation"
            )
        object.__setattr__(self, "proposal", _freeze(self.proposal))
        object.__setattr__(self, "evidence", _freeze(self.evidence))
        object.__setattr__(self, "provenance", _freeze(self.provenance))

    def to_context(self) -> dict[str, object]:
        return {
            "learning_write_adaptation_evaluation_execution_feedback_proposal_id": self.proposal_id,
            "learning_write_adaptation_evaluation_execution_feedback_decision_id": self.decision_id,
            "learning_write_adaptation_evaluation_execution_feedback_evaluation_id": self.evaluation_id,
            "learning_write_adaptation_feedback_evaluation_id": self.decision_source_evaluation_id,
            "learning_write_adaptation_evaluation_execution_feedback_id": self.feedback_id,
            "learning_write_adaptation_source_feedback_id": self.source_feedback_id,
            "learning_write_adaptation_candidate_id": self.candidate_id,
            "learning_candidate_id": self.source_candidate_id,
            "learning_write_adaptation_evaluation_execution_id": self.execution_id,
            "learning_write_adaptation_source_execution_id": self.source_execution_id,
            "learning_write_adaptation_evaluation_execution_preparation_id": self.preparation_id,
            "learning_write_adaptation_evaluation_proposal_admission_id": self.admission_id,
            "learning_write_adaptation_evaluation_proposal_id": self.proposal_source_id,
            "learning_write_adaptation_domain": self.domain,
            "learning_write_adaptation_evaluation_execution_policy_id": self.policy_id,
            "proposal": dict(self.proposal),
            "evidence": dict(self.evidence),
            "provenance": dict(self.provenance),
            "confidence": float(self.confidence),
            "reason": self.reason,
            "adaptation_authorized": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
            "memory_mutation_allowed": False,
            "authorization_granted": False,
        }


class LearningWriteAdaptationEvaluationExecutionFeedbackProposalService:
    """Create a proposal only from an accepted M22.38 decision."""

    def propose(
        self,
        context: LearningWriteAdaptationEvaluationExecutionFeedbackProposalContext,
    ) -> LearningWriteAdaptationEvaluationExecutionFeedbackProposal | None:
        if not isinstance(
            context,
            LearningWriteAdaptationEvaluationExecutionFeedbackProposalContext,
        ):
            raise TypeError(
                "context must be a LearningWriteAdaptationEvaluationExecutionFeedbackProposalContext"
            )

        decision = context.decision
        if decision.action is not LearningWriteAdaptationEvaluationExecutionFeedbackAction.ACCEPT:
            return None

        proposal_payload = dict(context.proposal)
        evidence = {
            "decision_action": decision.action.value,
            "decision_reason": decision.reason,
            "decision_confidence": decision.confidence,
            "evaluation_id": decision.evaluation_id,
            "evaluation_id_from_feedback": decision.decision_source_evaluation_id,
        }
        provenance = {
            "source": "adaptation_evaluation_execution_feedback_decision",
            "decision_id": decision.decision_id,
            "evaluation_id": decision.evaluation_id,
            "evaluation_id_from_feedback": decision.decision_source_evaluation_id,
            "feedback_id": decision.feedback_id,
            "source_feedback_id": decision.source_feedback_id,
            "candidate_id": decision.candidate_id,
            "source_candidate_id": decision.source_candidate_id,
            "execution_id": decision.execution_id,
            "source_execution_id": decision.source_execution_id,
            "preparation_id": decision.preparation_id,
            "admission_id": decision.admission_id,
            "proposal_source_id": decision.proposal_id,
            "policy_id": decision.policy_id,
        }
        proposal_id = self._proposal_id(decision, proposal_payload)
        return LearningWriteAdaptationEvaluationExecutionFeedbackProposal(
            proposal_id=proposal_id,
            decision_id=decision.decision_id,
            evaluation_id=decision.evaluation_id,
            decision_source_evaluation_id=decision.decision_source_evaluation_id,
            feedback_id=decision.feedback_id,
            source_feedback_id=decision.source_feedback_id,
            candidate_id=decision.candidate_id,
            source_candidate_id=decision.source_candidate_id,
            execution_id=decision.execution_id,
            source_execution_id=decision.source_execution_id,
            preparation_id=decision.preparation_id,
            admission_id=decision.admission_id,
            proposal_source_id=decision.proposal_id,
            domain=decision.domain,
            policy_id=decision.policy_id,
            proposal=proposal_payload,
            evidence=evidence,
            provenance=provenance,
            confidence=float(decision.confidence),
            reason="accepted future adaptation execution feedback decision creates a downstream proposal",
        )

    @staticmethod
    def _proposal_id(
        decision: LearningWriteAdaptationEvaluationExecutionFeedbackDecision,
        proposal: Mapping[str, Any],
    ) -> str:
        payload = json.dumps(
            {
                "decision_id": decision.decision_id,
                "evaluation_id": decision.evaluation_id,
                "decision_source_evaluation_id": decision.decision_source_evaluation_id,
                "feedback_id": decision.feedback_id,
                "source_feedback_id": decision.source_feedback_id,
                "candidate_id": decision.candidate_id,
                "execution_id": decision.execution_id,
                "preparation_id": decision.preparation_id,
                "admission_id": decision.admission_id,
                "proposal_source_id": decision.proposal_id,
                "domain": decision.domain,
                "policy_id": decision.policy_id,
                "proposal": proposal,
            },
            sort_keys=True,
            default=repr,
            separators=(",", ":"),
        ).encode("utf-8")
        return (
            "adaptation-evaluation-execution-feedback-proposal-"
            f"{hashlib.sha256(payload).hexdigest()[:24]}"
        )
