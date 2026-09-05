"""Proposal boundary after the dedicated M22.54 adaptation evaluation decision.

M22.55 converts exactly one ACCEPT M22.54 decision into immutable advisory
proposal evidence. DEFER and REJECT produce no proposal. Proposal formation
does not authorize execution, retry, revocation, memory mutation, authority,
or adaptation truth. The historical M22.47 proposal namespace remains
untouched.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping

from .learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_preparation_execution_result_integrity_feedback_evaluation_decision import (
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecision,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionAction,
)


class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalError(ValueError):
    """Raised when the dedicated M22.55 proposal contract is invalid."""


class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalKind(str, Enum):
    """Proposal classification produced by M22.55."""

    ACCEPTED_EVALUATION_DECISION = "accepted_evaluation_decision"


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
class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposal:
    """Immutable advisory proposal derived from exactly one accepted M22.54 decision."""

    proposal_id: str
    decision_id: str
    evaluation_id: str
    feedback_id: str
    integrity_id: str
    execution_id: str
    preparation_id: str
    admission_id: str
    proposal_source_id: str
    decision_source_evaluation_id: str
    evaluation_id_from_feedback: str
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
    kind: LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalKind
    action: LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionAction
    confidence: float
    reason: str
    payload: Mapping[str, Any]
    evidence: Mapping[str, Any]
    provenance: Mapping[str, str]
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for field_name in (
            "proposal_id", "decision_id", "evaluation_id", "feedback_id", "integrity_id",
            "execution_id", "preparation_id", "admission_id", "proposal_source_id",
            "decision_source_evaluation_id", "evaluation_id_from_feedback", "source_feedback_id",
            "candidate_id", "source_candidate_id", "execution_source_id", "source_execution_id",
            "source_admission_id", "source_proposal_id", "domain", "source_policy_id",
            "policy_id", "reason",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalError(
                    f"{field_name} must be a non-empty string"
                )
        if not isinstance(self.kind, LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalKind):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalError("invalid proposal kind")
        if not isinstance(self.action, LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionAction):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalError("invalid action")
        if self.action is not LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionAction.ACCEPT:
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalError("proposal must derive from ACCEPT")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalError("confidence must be numeric")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalError("confidence must be between 0.0 and 1.0")
        for field_name in ("payload", "evidence", "provenance", "metadata"):
            if not isinstance(getattr(self, field_name), Mapping):
                raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalError(f"{field_name} must be a mapping")
        if not self.payload:
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalError("payload must be non-empty")
        if not self.provenance:
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalError("provenance must be non-empty")
        if not all(isinstance(k, str) and k.strip() and isinstance(v, str) and v.strip() for k, v in self.provenance.items()):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalError("provenance must contain non-empty string keys and values")
        object.__setattr__(self, "payload", _freeze(self.payload))
        object.__setattr__(self, "evidence", _freeze(self.evidence))
        object.__setattr__(self, "provenance", _freeze(self.provenance))
        object.__setattr__(self, "metadata", _freeze(self.metadata))

    def to_context(self) -> dict[str, object]:
        return {
            "learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_decision_proposal_id": self.proposal_id,
            "learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_decision_id": self.decision_id,
            "learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_id": self.evaluation_id,
            "learning_write_adaptation_evaluation_execution_feedback_id": self.feedback_id,
            "learning_write_adaptation_evaluation_execution_result_integrity_id": self.integrity_id,
            "learning_write_adaptation_evaluation_execution_id": self.execution_id,
            "learning_write_adaptation_evaluation_execution_preparation_id": self.preparation_id,
            "learning_write_adaptation_evaluation_execution_feedback_proposal_admission_id": self.admission_id,
            "learning_write_adaptation_evaluation_proposal_source_decision_proposal_id": self.proposal_source_id,
            "learning_write_adaptation_evaluation_feedback_decision_id": self.decision_source_evaluation_id,
            "learning_write_adaptation_evaluation_execution_feedback_source_evaluation_id": self.evaluation_id_from_feedback,
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
            "proposal_kind": self.kind.value,
            "action": self.action.value,
            "confidence": float(self.confidence),
            "reason": self.reason,
            "payload": dict(self.payload),
            "evidence": dict(self.evidence),
            "provenance": dict(self.provenance),
            "metadata": dict(self.metadata),
            "execution_authorized": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
            "memory_mutation_allowed": False,
            "authority_granted": False,
            "adaptation_truth_proven": False,
        }


class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalService:
    """Create a non-authorizing proposal from exactly one M22.54 decision."""

    def propose(
        self,
        decision: LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecision,
        payload: Mapping[str, Any],
        evidence: Mapping[str, Any] | None = None,
        provenance: Mapping[str, str] | None = None,
    ) -> LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposal | None:
        if not isinstance(decision, LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecision):
            raise TypeError("decision must be a LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecision")
        if decision.action is not LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionAction.ACCEPT:
            return None
        if not isinstance(payload, Mapping) or not payload:
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalError("payload must be a non-empty mapping")
        evidence_data = dict(evidence or {})
        provenance_data = dict(provenance or {"source": "learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_decision"})
        proposal_id = self._proposal_id(decision, payload, evidence_data)
        return LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposal(
            proposal_id=proposal_id,
            decision_id=decision.decision_id,
            evaluation_id=decision.evaluation_id,
            feedback_id=decision.feedback_id,
            integrity_id=decision.integrity_id,
            execution_id=decision.execution_id,
            preparation_id=decision.preparation_id,
            admission_id=decision.admission_id,
            proposal_source_id=decision.proposal_id,
            decision_source_evaluation_id=decision.decision_source_evaluation_id,
            evaluation_id_from_feedback=decision.evaluation_id_from_feedback,
            source_feedback_id=decision.source_feedback_id,
            candidate_id=decision.candidate_id,
            source_candidate_id=decision.source_candidate_id,
            execution_source_id=decision.execution_source_id,
            source_execution_id=decision.source_execution_id,
            source_admission_id=decision.source_admission_id,
            source_proposal_id=decision.source_proposal_id,
            domain=decision.domain,
            source_policy_id=decision.source_policy_id,
            policy_id=decision.policy_id,
            kind=LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalKind.ACCEPTED_EVALUATION_DECISION,
            action=decision.action,
            confidence=float(decision.confidence),
            reason="accepted adaptation evaluation decision converted into a downstream proposal",
            payload=payload,
            evidence=evidence_data,
            provenance=provenance_data,
            metadata={"provider": "m22.54", "proposal_authority": False},
        )

    @staticmethod
    def _proposal_id(decision: Any, payload: Mapping[str, Any], evidence: Mapping[str, Any]) -> str:
        serialized = json.dumps(
            {
                "decision_id": decision.decision_id,
                "evaluation_id": decision.evaluation_id,
                "feedback_id": decision.feedback_id,
                "integrity_id": decision.integrity_id,
                "execution_id": decision.execution_id,
                "payload": payload,
                "evidence": evidence,
            },
            sort_keys=True,
            default=repr,
            separators=(",", ":"),
        ).encode("utf-8")
        return "adaptation-evaluation-execution-feedback-result-integrity-feedback-evaluation-decision-proposal-" + hashlib.sha256(serialized).hexdigest()[:24]
