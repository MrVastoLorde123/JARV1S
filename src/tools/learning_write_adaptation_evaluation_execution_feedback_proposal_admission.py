"""Admission boundary after future-adaptation execution feedback proposal.

This module evaluates an immutable M22.39 proposal before any downstream
future-execution preparation boundary. Admission is policy evidence, not
execution authorization, retry authority, revocation, or memory mutation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping, Protocol

from .learning_write_adaptation_evaluation_execution_feedback_proposal import (
    LearningWriteAdaptationEvaluationExecutionFeedbackProposal,
)


class LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionError(ValueError):
    """Raised when the M22.40 admission contract is invalid."""


class LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionStatus(str, Enum):
    """Normalized admission status for an M22.39 proposal."""

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
class LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionContext:
    """Immutable context supplied to an M22.40 admission provider."""

    proposal: LearningWriteAdaptationEvaluationExecutionFeedbackProposal
    related_context: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(
            self.proposal,
            LearningWriteAdaptationEvaluationExecutionFeedbackProposal,
        ):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionError(
                "proposal must be a LearningWriteAdaptationEvaluationExecutionFeedbackProposal"
            )
        if not isinstance(self.related_context, Mapping):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionError(
                "related_context must be a mapping"
            )
        object.__setattr__(self, "related_context", _freeze(self.related_context))


@dataclass(frozen=True)
class LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmission:
    """Immutable admission result for one M22.39 proposal."""

    admission_id: str
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
    source_admission_id: str
    proposal_source_id: str
    domain: str
    source_policy_id: str
    policy_id: str
    status: LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionStatus
    reason: str
    confidence: float
    proposal: Mapping[str, Any]
    evidence: Mapping[str, Any]
    provenance: Mapping[str, str]
    metadata: Mapping[str, Any] = field(default_factory=dict)
    adaptation_authorized: bool = False
    authorization_granted: bool = False
    execution_requested: bool = False
    retry_requested: bool = False
    revocation_requested: bool = False
    memory_mutation_allowed: bool = False
    authority_granted: bool = False

    def __post_init__(self) -> None:
        for field_name, value in (
            ("admission_id", self.admission_id),
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
            ("source_admission_id", self.source_admission_id),
            ("proposal_source_id", self.proposal_source_id),
            ("domain", self.domain),
            ("source_policy_id", self.source_policy_id),
            ("policy_id", self.policy_id),
            ("reason", self.reason),
        ):
            if not isinstance(value, str) or not value.strip():
                raise LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionError(
                    f"{field_name} must be a non-empty string"
                )
        if not isinstance(
            self.status,
            LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionStatus,
        ):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionError(
                "status must be a LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionStatus member"
            )
        if not isinstance(self.confidence, (int, float)) or isinstance(self.confidence, bool):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionError(
                "confidence must be a number"
            )
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionError(
                "confidence must be between 0.0 and 1.0"
            )
        for field_name, value in (
            ("proposal", self.proposal),
            ("evidence", self.evidence),
        ):
            if not isinstance(value, Mapping):
                raise LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionError(
                    f"{field_name} must be a mapping"
                )
        if not isinstance(self.provenance, Mapping):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionError(
                "provenance must be a mapping"
            )
        if not isinstance(self.metadata, Mapping):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionError(
                "metadata must be a mapping"
            )
        if not all(
            isinstance(key, str)
            and key.strip()
            and isinstance(value, str)
            and value.strip()
            for key, value in self.provenance.items()
        ):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionError(
                "provenance must contain non-empty string keys and values"
            )
        if (
            self.adaptation_authorized
            or self.authorization_granted
            or self.execution_requested
            or self.retry_requested
            or self.revocation_requested
            or self.memory_mutation_allowed
            or self.authority_granted
        ):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionError(
                "admission cannot grant authorization, execution, retry, revocation, memory mutation, or general authority"
            )
        object.__setattr__(self, "proposal", _freeze(self.proposal))
        object.__setattr__(self, "evidence", _freeze(self.evidence))
        object.__setattr__(self, "provenance", _freeze(self.provenance))
        object.__setattr__(self, "metadata", _freeze(self.metadata))

    def to_context(self) -> dict[str, object]:
        return {
            "learning_write_adaptation_evaluation_execution_feedback_proposal_admission_id": self.admission_id,
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
            "learning_write_adaptation_evaluation_execution_source_admission_id": self.source_admission_id,
            "learning_write_adaptation_evaluation_proposal_id": self.proposal_source_id,
            "learning_write_adaptation_domain": self.domain,
            "learning_write_adaptation_source_policy_id": self.source_policy_id,
            "learning_write_adaptation_evaluation_execution_policy_id": self.policy_id,
            "adaptation_evaluation_execution_feedback_proposal_admission_status": self.status.value,
            "reason": self.reason,
            "confidence": float(self.confidence),
            "proposal": dict(self.proposal),
            "evidence": dict(self.evidence),
            "provenance": dict(self.provenance),
            "metadata": dict(self.metadata),
            "adaptation_authorized": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
            "memory_mutation_allowed": False,
            "authority_granted": False,
        }


class LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionProvider(Protocol):
    """Provider-neutral, non-mutating M22.40 admission interface."""

    def admit(
        self,
        context: LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionContext,
    ) -> LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmission:
        ...


class DeterministicLearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionProvider:
    """Deterministic baseline provider for M22.40 proposal admission."""

    _POLICY_ID = "adaptation-evaluation-execution-feedback-proposal-admission-baseline-v1"

    def admit(
        self,
        context: LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionContext,
    ) -> LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmission:
        proposal = context.proposal
        if proposal.confidence < 0.5:
            status = LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionStatus.REJECTED
            reason = "proposal confidence is below the deterministic admission threshold"
        elif not proposal.proposal:
            status = LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionStatus.REJECTED
            reason = "proposal payload is empty"
        elif not proposal.evidence:
            status = LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionStatus.REJECTED
            reason = "proposal evidence is empty"
        elif not proposal.provenance:
            status = LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionStatus.REJECTED
            reason = "proposal provenance is empty"
        else:
            status = LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionStatus.ADMITTED
            reason = "proposal satisfies deterministic admission requirements"

        admission_id = self._admission_id(proposal, status, reason)
        return LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmission(
            admission_id=admission_id,
            proposal_id=proposal.proposal_id,
            decision_id=proposal.decision_id,
            evaluation_id=proposal.evaluation_id,
            decision_source_evaluation_id=proposal.decision_source_evaluation_id,
            feedback_id=proposal.feedback_id,
            source_feedback_id=proposal.source_feedback_id,
            candidate_id=proposal.candidate_id,
            source_candidate_id=proposal.source_candidate_id,
            execution_id=proposal.execution_id,
            source_execution_id=proposal.source_execution_id,
            preparation_id=proposal.preparation_id,
            source_admission_id=proposal.admission_id,
            proposal_source_id=proposal.proposal_source_id,
            domain=proposal.domain,
            source_policy_id=proposal.policy_id,
            policy_id=self._POLICY_ID,
            status=status,
            reason=reason,
            confidence=float(proposal.confidence),
            proposal=proposal.proposal,
            evidence=proposal.evidence,
            provenance=proposal.provenance,
            metadata={"provider": "deterministic"},
        )

    @staticmethod
    def _admission_id(
        proposal: LearningWriteAdaptationEvaluationExecutionFeedbackProposal,
        status: LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionStatus,
        reason: str,
    ) -> str:
        payload = json.dumps(
            {
                "proposal_id": proposal.proposal_id,
                "decision_id": proposal.decision_id,
                "evaluation_id": proposal.evaluation_id,
                "feedback_id": proposal.feedback_id,
                "preparation_id": proposal.preparation_id,
                "status": status.value,
                "reason": reason,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return (
            "adaptation-evaluation-execution-feedback-proposal-admission-"
            f"{hashlib.sha256(payload).hexdigest()[:24]}"
        )


class LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionService:
    """Validate and obtain a non-authorizing M22.40 admission result."""

    def __init__(
        self,
        provider: LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionProvider | None = None,
    ) -> None:
        self._provider = provider or DeterministicLearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionProvider()

    def admit(
        self,
        context: LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionContext,
    ) -> LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmission:
        if not isinstance(
            context,
            LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionContext,
        ):
            raise TypeError(
                "context must be a LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionContext"
            )

        admission = self._provider.admit(context)
        if not isinstance(
            admission,
            LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmission,
        ):
            raise TypeError(
                "provider must return a LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmission"
            )

        proposal = context.proposal
        expected = (
            ("proposal", admission.proposal_id, proposal.proposal_id),
            ("decision", admission.decision_id, proposal.decision_id),
            ("evaluation", admission.evaluation_id, proposal.evaluation_id),
            (
                "decision source evaluation",
                admission.decision_source_evaluation_id,
                proposal.decision_source_evaluation_id,
            ),
            ("feedback", admission.feedback_id, proposal.feedback_id),
            ("source feedback", admission.source_feedback_id, proposal.source_feedback_id),
            ("candidate", admission.candidate_id, proposal.candidate_id),
            ("source candidate", admission.source_candidate_id, proposal.source_candidate_id),
            ("execution", admission.execution_id, proposal.execution_id),
            ("source execution", admission.source_execution_id, proposal.source_execution_id),
            ("preparation", admission.preparation_id, proposal.preparation_id),
            ("source admission", admission.source_admission_id, proposal.admission_id),
            ("proposal source", admission.proposal_source_id, proposal.proposal_source_id),
            ("domain", admission.domain, proposal.domain),
            ("source policy", admission.source_policy_id, proposal.policy_id),
        )
        for label, actual, expected_value in expected:
            if actual != expected_value:
                raise LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionError(
                    f"admission {label} identity mismatch"
                )
        return admission
