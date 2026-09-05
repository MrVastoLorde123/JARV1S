"""Admission boundary after adaptation-evaluation proposal.

This module evaluates an immutable adaptation-evaluation proposal before any
future execution or mutation boundary. Admission is identity-bound evidence,
not authorization or execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping, Protocol

from .learning_write_adaptation_evaluation_proposal import (
    LearningWriteAdaptationEvaluationProposal,
)


class LearningWriteAdaptationEvaluationProposalAdmissionError(ValueError):
    """Raised when the adaptation-evaluation proposal admission contract is invalid."""


class LearningWriteAdaptationEvaluationProposalAdmissionStatus(str, Enum):
    """Normalized admission status for an adaptation-evaluation proposal."""

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
class LearningWriteAdaptationEvaluationProposalAdmissionContext:
    """Immutable context supplied to an admission provider."""

    proposal: LearningWriteAdaptationEvaluationProposal
    related_context: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(
            self.proposal, LearningWriteAdaptationEvaluationProposal
        ):
            raise LearningWriteAdaptationEvaluationProposalAdmissionError(
                "proposal must be a LearningWriteAdaptationEvaluationProposal"
            )
        if not isinstance(self.related_context, Mapping):
            raise LearningWriteAdaptationEvaluationProposalAdmissionError(
                "related_context must be a mapping"
            )
        object.__setattr__(self, "related_context", _freeze(self.related_context))


@dataclass(frozen=True)
class LearningWriteAdaptationEvaluationProposalAdmission:
    """Immutable admission result for one evaluation proposal."""

    admission_id: str
    proposal_id: str
    decision_id: str
    evaluation_id: str
    feedback_id: str
    source_feedback_id: str
    candidate_id: str
    execution_id: str
    source_candidate_id: str
    domain: str
    status: LearningWriteAdaptationEvaluationProposalAdmissionStatus
    reason: str
    confidence: float
    policy_id: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
    authorization_granted: bool = False
    execution_requested: bool = False
    memory_mutation_allowed: bool = False

    def __post_init__(self) -> None:
        for field_name, value in (
            ("admission_id", self.admission_id),
            ("proposal_id", self.proposal_id),
            ("decision_id", self.decision_id),
            ("evaluation_id", self.evaluation_id),
            ("feedback_id", self.feedback_id),
            ("source_feedback_id", self.source_feedback_id),
            ("candidate_id", self.candidate_id),
            ("execution_id", self.execution_id),
            ("source_candidate_id", self.source_candidate_id),
            ("domain", self.domain),
            ("reason", self.reason),
            ("policy_id", self.policy_id),
        ):
            if not isinstance(value, str) or not value.strip():
                raise LearningWriteAdaptationEvaluationProposalAdmissionError(
                    f"{field_name} must be a non-empty string"
                )
        if not isinstance(
            self.status,
            LearningWriteAdaptationEvaluationProposalAdmissionStatus,
        ):
            raise LearningWriteAdaptationEvaluationProposalAdmissionError(
                "status must be a LearningWriteAdaptationEvaluationProposalAdmissionStatus member"
            )
        if not isinstance(self.confidence, (int, float)) or isinstance(self.confidence, bool):
            raise LearningWriteAdaptationEvaluationProposalAdmissionError(
                "confidence must be a number"
            )
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise LearningWriteAdaptationEvaluationProposalAdmissionError(
                "confidence must be between 0.0 and 1.0"
            )
        if not isinstance(self.metadata, Mapping):
            raise LearningWriteAdaptationEvaluationProposalAdmissionError(
                "metadata must be a mapping"
            )
        if self.authorization_granted or self.execution_requested or self.memory_mutation_allowed:
            raise LearningWriteAdaptationEvaluationProposalAdmissionError(
                "admission cannot grant authorization, execution, or memory mutation"
            )
        object.__setattr__(self, "metadata", _freeze(self.metadata))

    def to_context(self) -> dict[str, object]:
        return {
            "learning_write_adaptation_evaluation_proposal_admission_id": self.admission_id,
            "learning_write_adaptation_evaluation_proposal_id": self.proposal_id,
            "learning_write_adaptation_evaluation_decision_id": self.decision_id,
            "learning_write_adaptation_feedback_evaluation_id": self.evaluation_id,
            "learning_write_adaptation_feedback_id": self.feedback_id,
            "learning_write_adaptation_source_feedback_id": self.source_feedback_id,
            "learning_write_adaptation_candidate_id": self.candidate_id,
            "learning_write_adaptation_execution_id": self.execution_id,
            "learning_candidate_id": self.source_candidate_id,
            "learning_write_adaptation_domain": self.domain,
            "adaptation_evaluation_proposal_admission_status": self.status.value,
            "reason": self.reason,
            "confidence": float(self.confidence),
            "policy_id": self.policy_id,
            "metadata": dict(self.metadata),
            "authorization_granted": False,
            "execution_requested": False,
            "memory_mutated": False,
            "retry_requested": False,
            "revocation_requested": False,
        }


class LearningWriteAdaptationEvaluationProposalAdmissionProvider(Protocol):
    """Provider-neutral admission interface."""

    def admit(
        self,
        context: LearningWriteAdaptationEvaluationProposalAdmissionContext,
    ) -> LearningWriteAdaptationEvaluationProposalAdmission:
        ...


class DeterministicLearningWriteAdaptationEvaluationProposalAdmissionProvider:
    """Deterministic baseline provider for proposal admission."""

    _POLICY_ID = "adaptation-evaluation-proposal-baseline-v1"

    def admit(
        self,
        context: LearningWriteAdaptationEvaluationProposalAdmissionContext,
    ) -> LearningWriteAdaptationEvaluationProposalAdmission:
        proposal = context.proposal
        if proposal.confidence < 0.5:
            status = LearningWriteAdaptationEvaluationProposalAdmissionStatus.REJECTED
            reason = "proposal confidence is below the deterministic admission threshold"
        elif not proposal.proposal:
            status = LearningWriteAdaptationEvaluationProposalAdmissionStatus.REJECTED
            reason = "proposal payload is empty"
        elif not proposal.evidence:
            status = LearningWriteAdaptationEvaluationProposalAdmissionStatus.REJECTED
            reason = "proposal evidence is empty"
        elif not proposal.provenance:
            status = LearningWriteAdaptationEvaluationProposalAdmissionStatus.REJECTED
            reason = "proposal provenance is empty"
        else:
            status = LearningWriteAdaptationEvaluationProposalAdmissionStatus.ADMITTED
            reason = "proposal satisfies deterministic admission requirements"

        admission_id = self._admission_id(proposal, status, reason)
        return LearningWriteAdaptationEvaluationProposalAdmission(
            admission_id=admission_id,
            proposal_id=proposal.proposal_id,
            decision_id=proposal.decision_id,
            evaluation_id=proposal.evaluation_id,
            feedback_id=proposal.feedback_id,
            source_feedback_id=proposal.source_feedback_id,
            candidate_id=proposal.candidate_id,
            execution_id=proposal.execution_id,
            source_candidate_id=proposal.source_candidate_id,
            domain=proposal.domain,
            status=status,
            reason=reason,
            confidence=float(proposal.confidence),
            policy_id=self._POLICY_ID,
            metadata={"provider": "deterministic"},
        )

    @staticmethod
    def _admission_id(
        proposal: LearningWriteAdaptationEvaluationProposal,
        status: LearningWriteAdaptationEvaluationProposalAdmissionStatus,
        reason: str,
    ) -> str:
        payload = json.dumps(
            {
                "proposal_id": proposal.proposal_id,
                "decision_id": proposal.decision_id,
                "evaluation_id": proposal.evaluation_id,
                "status": status.value,
                "reason": reason,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return f"adaptation-evaluation-proposal-admission-{hashlib.sha256(payload).hexdigest()[:24]}"


class LearningWriteAdaptationEvaluationProposalAdmissionService:
    """Validate and obtain a non-authorizing admission result."""

    def __init__(
        self,
        provider: LearningWriteAdaptationEvaluationProposalAdmissionProvider | None = None,
    ) -> None:
        self._provider = provider or DeterministicLearningWriteAdaptationEvaluationProposalAdmissionProvider()

    def admit(
        self,
        context: LearningWriteAdaptationEvaluationProposalAdmissionContext,
    ) -> LearningWriteAdaptationEvaluationProposalAdmission:
        if not isinstance(context, LearningWriteAdaptationEvaluationProposalAdmissionContext):
            raise TypeError(
                "context must be a LearningWriteAdaptationEvaluationProposalAdmissionContext"
            )

        admission = self._provider.admit(context)
        if not isinstance(admission, LearningWriteAdaptationEvaluationProposalAdmission):
            raise TypeError(
                "provider must return a LearningWriteAdaptationEvaluationProposalAdmission"
            )

        proposal = context.proposal
        expected = (
            ("proposal", admission.proposal_id, proposal.proposal_id),
            ("decision", admission.decision_id, proposal.decision_id),
            ("evaluation", admission.evaluation_id, proposal.evaluation_id),
            ("feedback", admission.feedback_id, proposal.feedback_id),
            ("source feedback", admission.source_feedback_id, proposal.source_feedback_id),
            ("candidate", admission.candidate_id, proposal.candidate_id),
            ("execution", admission.execution_id, proposal.execution_id),
            ("source candidate", admission.source_candidate_id, proposal.source_candidate_id),
            ("domain", admission.domain, proposal.domain),
        )
        for label, actual, expected_value in expected:
            if actual != expected_value:
                raise LearningWriteAdaptationEvaluationProposalAdmissionError(
                    f"admission {label} identity mismatch"
                )
        return admission
