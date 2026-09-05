"""M22.56: adaptation evaluation decision proposal -> admission.

Admission is policy evidence only. It does not authorize execution, request
execution, retry, revoke, mutate memory, grant authority, or establish truth.
The historical M22.48 namespace remains untouched.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping, Protocol

from .learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_preparation_execution_result_integrity_feedback_evaluation_decision_proposal import (
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposal,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalKind,
)


class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionError(ValueError):
    """Raised when the dedicated M22.56 admission contract is invalid."""


class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionStatus(str, Enum):
    ADMITTED = "admitted"
    REJECTED = "rejected"


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
class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionContext:
    proposal: LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposal
    related_context: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.proposal, LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposal):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionError(
                "proposal must be a LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposal"
            )
        if not isinstance(self.related_context, Mapping):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionError(
                "related_context must be a mapping"
            )
        object.__setattr__(self, "related_context", _freeze(self.related_context))


@dataclass(frozen=True)
class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmission:
    admission_id: str
    proposal_id: str
    decision_id: str
    evaluation_id: str
    feedback_id: str
    integrity_id: str
    execution_id: str
    preparation_id: str
    proposal_source_id: str
    source_proposal_id: str
    decision_source_evaluation_id: str
    evaluation_id_from_feedback: str
    source_feedback_id: str
    candidate_id: str
    source_candidate_id: str
    execution_source_id: str
    source_execution_id: str
    source_admission_id: str
    domain: str
    source_policy_id: str
    policy_id: str
    status: LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionStatus
    reason: str
    confidence: float
    proposal: Mapping[str, Any]
    evidence: Mapping[str, Any]
    provenance: Mapping[str, str]
    metadata: Mapping[str, Any] = field(default_factory=dict)
    execution_authorized: bool = False
    authorization_granted: bool = False
    execution_requested: bool = False
    retry_requested: bool = False
    revocation_requested: bool = False
    memory_mutation_allowed: bool = False
    authority_granted: bool = False

    def __post_init__(self) -> None:
        string_fields = (
            "admission_id", "proposal_id", "decision_id", "evaluation_id", "feedback_id",
            "integrity_id", "execution_id", "preparation_id", "proposal_source_id",
            "source_proposal_id", "decision_source_evaluation_id", "evaluation_id_from_feedback",
            "source_feedback_id", "candidate_id", "source_candidate_id", "execution_source_id",
            "source_execution_id", "source_admission_id", "domain", "source_policy_id",
            "policy_id", "reason",
        )
        for field_name in string_fields:
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionError(
                    f"{field_name} must be a non-empty string"
                )
        if not isinstance(self.status, LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionStatus):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionError("invalid admission status")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionError("confidence must be numeric")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionError("confidence must be between 0.0 and 1.0")
        for field_name in ("proposal", "evidence", "provenance", "metadata"):
            if not isinstance(getattr(self, field_name), Mapping):
                raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionError(f"{field_name} must be a mapping")
        if self.status is LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionStatus.ADMITTED:
            if not self.proposal:
                raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionError("admitted proposal payload cannot be empty")
            if not self.provenance:
                raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionError("admitted proposal provenance cannot be empty")
        if not all(isinstance(k, str) and k.strip() and isinstance(v, str) and v.strip() for k, v in self.provenance.items()):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionError("provenance must contain non-empty string keys and values")
        if any((self.execution_authorized, self.authorization_granted, self.execution_requested, self.retry_requested, self.revocation_requested, self.memory_mutation_allowed, self.authority_granted)):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionError("admission cannot grant authorization, execution, retry, revocation, memory mutation, or general authority")
        object.__setattr__(self, "proposal", _freeze(self.proposal))
        object.__setattr__(self, "evidence", _freeze(self.evidence))
        object.__setattr__(self, "provenance", _freeze(self.provenance))
        object.__setattr__(self, "metadata", _freeze(self.metadata))

    def to_context(self) -> dict[str, object]:
        return {
            "learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_decision_proposal_admission_id": self.admission_id,
            "learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_decision_proposal_id": self.proposal_id,
            "learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_decision_id": self.decision_id,
            "learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_id": self.evaluation_id,
            "learning_write_adaptation_evaluation_execution_feedback_id": self.feedback_id,
            "learning_write_adaptation_evaluation_execution_result_integrity_id": self.integrity_id,
            "learning_write_adaptation_evaluation_execution_id": self.execution_id,
            "learning_write_adaptation_evaluation_execution_preparation_id": self.preparation_id,
            "learning_write_adaptation_evaluation_proposal_source_decision_proposal_id": self.proposal_source_id,
            "learning_write_adaptation_evaluation_proposal_id": self.source_proposal_id,
            "learning_write_adaptation_evaluation_feedback_decision_source_evaluation_id": self.decision_source_evaluation_id,
            "learning_write_adaptation_evaluation_execution_feedback_source_evaluation_id": self.evaluation_id_from_feedback,
            "learning_write_adaptation_evaluation_execution_feedback_source_feedback_id": self.source_feedback_id,
            "learning_write_adaptation_candidate_id": self.candidate_id,
            "learning_candidate_id": self.source_candidate_id,
            "learning_write_adaptation_evaluation_execution_source_id": self.execution_source_id,
            "learning_write_adaptation_source_execution_id": self.source_execution_id,
            "learning_write_adaptation_evaluation_execution_source_admission_id": self.source_admission_id,
            "learning_write_adaptation_domain": self.domain,
            "learning_write_adaptation_source_policy_id": self.source_policy_id,
            "learning_write_adaptation_evaluation_execution_policy_id": self.policy_id,
            "adaptation_evaluation_decision_proposal_admission_status": self.status.value,
            "reason": self.reason,
            "confidence": float(self.confidence),
            "proposal": dict(self.proposal),
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


class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionProvider(Protocol):
    def admit(self, context: LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionContext) -> LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmission:
        ...


class DeterministicLearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionProvider:
    _POLICY_ID = "adaptation-evaluation-decision-proposal-admission-baseline-v1"

    def admit(self, context: LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionContext) -> LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmission:
        proposal = context.proposal
        if proposal.kind is not LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalKind.ACCEPTED_EVALUATION_DECISION:
            status = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionStatus.REJECTED
            reason = "unsupported proposal kind"
        elif proposal.action.value != "accept":
            status = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionStatus.REJECTED
            reason = "proposal action is not admissible"
        elif proposal.confidence < 0.5:
            status = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionStatus.REJECTED
            reason = "proposal confidence is below the deterministic admission threshold"
        elif not proposal.payload:
            status = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionStatus.REJECTED
            reason = "proposal payload is empty"
        elif not proposal.provenance:
            status = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionStatus.REJECTED
            reason = "proposal provenance is empty"
        else:
            status = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionStatus.ADMITTED
            reason = "proposal satisfies deterministic admission requirements"
        admission_id = self._admission_id(proposal, status, reason)
        return LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmission(
            admission_id=admission_id,
            proposal_id=proposal.proposal_id,
            decision_id=proposal.decision_id,
            evaluation_id=proposal.evaluation_id,
            feedback_id=proposal.feedback_id,
            integrity_id=proposal.integrity_id,
            execution_id=proposal.execution_id,
            preparation_id=proposal.preparation_id,
            proposal_source_id=proposal.proposal_source_id,
            source_proposal_id=proposal.source_proposal_id,
            decision_source_evaluation_id=proposal.decision_source_evaluation_id,
            evaluation_id_from_feedback=proposal.evaluation_id_from_feedback,
            source_feedback_id=proposal.source_feedback_id,
            candidate_id=proposal.candidate_id,
            source_candidate_id=proposal.source_candidate_id,
            execution_source_id=proposal.execution_source_id,
            source_execution_id=proposal.source_execution_id,
            source_admission_id=proposal.admission_id,
            domain=proposal.domain,
            source_policy_id=proposal.policy_id,
            policy_id=self._POLICY_ID,
            status=status,
            reason=reason,
            confidence=float(proposal.confidence),
            proposal=proposal.payload,
            evidence=proposal.evidence,
            provenance=proposal.provenance,
            metadata={"provider": "deterministic", "proposal_kind": proposal.kind.value},
        )

    @staticmethod
    def _admission_id(proposal: Any, status: LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionStatus, reason: str) -> str:
        serialized = json.dumps({
            "proposal_id": proposal.proposal_id,
            "decision_id": proposal.decision_id,
            "evaluation_id": proposal.evaluation_id,
            "feedback_id": proposal.feedback_id,
            "integrity_id": proposal.integrity_id,
            "status": status.value,
            "reason": reason,
        }, sort_keys=True, default=repr, separators=(",", ":")).encode("utf-8")
        return "adaptation-evaluation-execution-feedback-result-integrity-feedback-evaluation-decision-proposal-admission-" + hashlib.sha256(serialized).hexdigest()[:24]


class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionService:
    def __init__(self, provider: LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionProvider | None = None) -> None:
        self._provider = provider or DeterministicLearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionProvider()

    def admit(self, context: LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionContext) -> LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmission:
        if not isinstance(context, LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionContext):
            raise TypeError("context must be a LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionContext")
        admission = self._provider.admit(context)
        if not isinstance(admission, LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmission):
            raise TypeError("provider must return an M22.56 admission artifact")
        proposal = context.proposal
        expected = (
            ("proposal", admission.proposal_id, proposal.proposal_id),
            ("decision", admission.decision_id, proposal.decision_id),
            ("evaluation", admission.evaluation_id, proposal.evaluation_id),
            ("feedback", admission.feedback_id, proposal.feedback_id),
            ("integrity", admission.integrity_id, proposal.integrity_id),
            ("execution", admission.execution_id, proposal.execution_id),
            ("preparation", admission.preparation_id, proposal.preparation_id),
            ("proposal source", admission.proposal_source_id, proposal.proposal_source_id),
            ("source proposal", admission.source_proposal_id, proposal.source_proposal_id),
            ("decision source evaluation", admission.decision_source_evaluation_id, proposal.decision_source_evaluation_id),
            ("evaluation from feedback", admission.evaluation_id_from_feedback, proposal.evaluation_id_from_feedback),
            ("source feedback", admission.source_feedback_id, proposal.source_feedback_id),
            ("candidate", admission.candidate_id, proposal.candidate_id),
            ("source candidate", admission.source_candidate_id, proposal.source_candidate_id),
            ("execution source", admission.execution_source_id, proposal.execution_source_id),
            ("source execution", admission.source_execution_id, proposal.source_execution_id),
            ("source admission", admission.source_admission_id, proposal.admission_id),
            ("domain", admission.domain, proposal.domain),
            ("source policy", admission.source_policy_id, proposal.policy_id),
        )
        for label, actual, expected_value in expected:
            if actual != expected_value:
                raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionError(f"admission {label} identity mismatch")
        return admission
