"""Admission boundary after adaptation proposal.

This module evaluates whether an adaptation proposal is structurally
admissible for a later adaptation execution boundary. It does not apply the
adaptation, mutate learning or memory, authorize tools, retry, or revoke.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping, Protocol

from .learning_write_adaptation_proposal import LearningWriteAdaptationProposal


class LearningWriteAdaptationAdmissionError(ValueError):
    """Raised when the adaptation-admission contract is invalid."""


class LearningWriteAdaptationAdmissionStatus(str, Enum):
    """Admission result for an adaptation proposal."""

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
class LearningWriteAdaptationAdmissionContext:
    """Immutable context supplied to an adaptation-admission provider."""

    proposal: LearningWriteAdaptationProposal
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.proposal, LearningWriteAdaptationProposal):
            raise LearningWriteAdaptationAdmissionError(
                "proposal must be a LearningWriteAdaptationProposal"
            )
        if not isinstance(self.metadata, Mapping):
            raise LearningWriteAdaptationAdmissionError("metadata must be a mapping")
        object.__setattr__(self, "metadata", _freeze(self.metadata))


@dataclass(frozen=True)
class LearningWriteAdaptationAdmission:
    """Immutable admission result that grants no execution authority."""

    admission_id: str
    proposal_id: str
    decision_id: str
    candidate_id: str
    feedback_id: str
    execution_id: str
    domain: str
    status: LearningWriteAdaptationAdmissionStatus
    reason: str
    confidence: float
    policy_id: str
    adaptation_write_allowed: bool = False
    memory_mutation_allowed: bool = False
    authority_granted: bool = False

    def __post_init__(self) -> None:
        for field_name, value in (
            ("admission_id", self.admission_id),
            ("proposal_id", self.proposal_id),
            ("decision_id", self.decision_id),
            ("candidate_id", self.candidate_id),
            ("feedback_id", self.feedback_id),
            ("execution_id", self.execution_id),
            ("domain", self.domain),
            ("reason", self.reason),
            ("policy_id", self.policy_id),
        ):
            if not isinstance(value, str) or not value.strip():
                raise LearningWriteAdaptationAdmissionError(
                    f"{field_name} must be a non-empty string"
                )
        if not isinstance(self.status, LearningWriteAdaptationAdmissionStatus):
            raise LearningWriteAdaptationAdmissionError(
                "status must be a LearningWriteAdaptationAdmissionStatus member"
            )
        if not isinstance(self.confidence, (int, float)) or isinstance(self.confidence, bool):
            raise LearningWriteAdaptationAdmissionError("confidence must be a number")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise LearningWriteAdaptationAdmissionError(
                "confidence must be between 0.0 and 1.0"
            )
        if self.adaptation_write_allowed or self.memory_mutation_allowed or self.authority_granted:
            raise LearningWriteAdaptationAdmissionError(
                "adaptation admission cannot grant write, mutation, or authority"
            )

    def to_context(self) -> dict[str, object]:
        return {
            "learning_write_adaptation_admission_id": self.admission_id,
            "learning_write_adaptation_proposal_id": self.proposal_id,
            "learning_write_adaptation_decision_id": self.decision_id,
            "learning_write_adaptation_candidate_id": self.candidate_id,
            "learning_write_feedback_id": self.feedback_id,
            "learning_write_execution_id": self.execution_id,
            "learning_write_domain": self.domain,
            "admission_status": self.status.value,
            "reason": self.reason,
            "confidence": float(self.confidence),
            "policy_id": self.policy_id,
            "adaptation_write_allowed": False,
            "memory_mutation_allowed": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
        }


class LearningWriteAdaptationAdmissionProvider(Protocol):
    """Provider-neutral, non-mutating adaptation-admission interface."""

    def admit(
        self, context: LearningWriteAdaptationAdmissionContext
    ) -> LearningWriteAdaptationAdmission:
        ...


class DeterministicLearningWriteAdaptationAdmissionProvider:
    """Conservative structural admission policy for adaptation proposals."""

    POLICY_ID = "deterministic-adaptation-baseline"
    MIN_CONFIDENCE = 0.5

    def admit(
        self, context: LearningWriteAdaptationAdmissionContext
    ) -> LearningWriteAdaptationAdmission:
        proposal = context.proposal
        if not proposal.adaptation:
            status = LearningWriteAdaptationAdmissionStatus.REJECTED
            reason = "adaptation proposal must contain a non-empty adaptation"
        elif not proposal.evidence:
            status = LearningWriteAdaptationAdmissionStatus.REJECTED
            reason = "adaptation proposal requires evidence"
        elif not proposal.provenance:
            status = LearningWriteAdaptationAdmissionStatus.REJECTED
            reason = "adaptation proposal requires provenance"
        elif float(proposal.confidence) < self.MIN_CONFIDENCE:
            status = LearningWriteAdaptationAdmissionStatus.REJECTED
            reason = "adaptation proposal confidence is below admission threshold"
        else:
            status = LearningWriteAdaptationAdmissionStatus.ADMITTED
            reason = "adaptation proposal satisfies deterministic structural admission requirements"

        admission_id = self._admission_id(proposal, status, reason)
        return LearningWriteAdaptationAdmission(
            admission_id=admission_id,
            proposal_id=proposal.proposal_id,
            decision_id=proposal.decision_id,
            candidate_id=proposal.candidate_id,
            feedback_id=proposal.feedback_id,
            execution_id=proposal.execution_id,
            domain=proposal.domain,
            status=status,
            reason=reason,
            confidence=float(proposal.confidence),
            policy_id=self.POLICY_ID,
        )

    @staticmethod
    def _admission_id(
        proposal: LearningWriteAdaptationProposal,
        status: LearningWriteAdaptationAdmissionStatus,
        reason: str,
    ) -> str:
        payload = json.dumps(
            {
                "proposal_id": proposal.proposal_id,
                "decision_id": proposal.decision_id,
                "candidate_id": proposal.candidate_id,
                "status": status.value,
                "reason": reason,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return f"learn-write-adaptation-admission-{hashlib.sha256(payload).hexdigest()[:24]}"


class LearningWriteAdaptationAdmissionService:
    """Validate an adaptation proposal through a replaceable admission provider."""

    def __init__(
        self,
        provider: LearningWriteAdaptationAdmissionProvider | None = None,
    ) -> None:
        self._provider = provider or DeterministicLearningWriteAdaptationAdmissionProvider()

    def admit(
        self,
        context: LearningWriteAdaptationAdmissionContext,
    ) -> LearningWriteAdaptationAdmission:
        if not isinstance(context, LearningWriteAdaptationAdmissionContext):
            raise TypeError("context must be a LearningWriteAdaptationAdmissionContext")

        admission = self._provider.admit(context)
        if not isinstance(admission, LearningWriteAdaptationAdmission):
            raise TypeError(
                "provider must return a LearningWriteAdaptationAdmission"
            )

        proposal = context.proposal
        if admission.proposal_id != proposal.proposal_id:
            raise LearningWriteAdaptationAdmissionError("admission proposal identity mismatch")
        if admission.decision_id != proposal.decision_id:
            raise LearningWriteAdaptationAdmissionError("admission decision identity mismatch")
        if admission.candidate_id != proposal.candidate_id:
            raise LearningWriteAdaptationAdmissionError("admission candidate identity mismatch")
        if admission.feedback_id != proposal.feedback_id:
            raise LearningWriteAdaptationAdmissionError("admission feedback identity mismatch")
        if admission.execution_id != proposal.execution_id:
            raise LearningWriteAdaptationAdmissionError("admission execution identity mismatch")
        if admission.domain != proposal.domain:
            raise LearningWriteAdaptationAdmissionError("admission domain identity mismatch")
        return admission
