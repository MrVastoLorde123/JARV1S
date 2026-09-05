"""Learning-write admission boundary after an inert write proposal.

This module decides whether a ``LearningWriteProposal`` is structurally and
policy-wise admissible for a later write executor. It does not persist
learning, mutate memory, authorize execution, retry, revoke, or execute tools.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from typing import Any, Mapping

from .learning_write_proposal import LearningWriteDomain, LearningWriteProposal


class LearningWriteAdmissionError(ValueError):
    """Raised when the learning-write admission contract is invalid."""


class LearningWriteAdmissionStatus(str, Enum):
    """Whether a learning-write proposal may proceed to a later writer."""

    ADMITTED = "admitted"
    REJECTED = "rejected"


@dataclass(frozen=True)
class LearningWriteAdmissionContext:
    """Provider-neutral policy context for one exact write proposal."""

    proposal: LearningWriteProposal
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class LearningWriteAdmission:
    """Immutable admission result with no mutation or authority."""

    admission_id: str
    proposal_id: str
    decision_id: str
    candidate_id: str
    domain: LearningWriteDomain
    status: LearningWriteAdmissionStatus
    reason: str
    confidence: float
    policy_id: str
    learning_write_allowed: bool = False
    memory_mutated: bool = False
    authority_granted: bool = False

    def __post_init__(self) -> None:
        for field_name, value in (
            ("admission_id", self.admission_id),
            ("proposal_id", self.proposal_id),
            ("decision_id", self.decision_id),
            ("candidate_id", self.candidate_id),
            ("reason", self.reason),
            ("policy_id", self.policy_id),
        ):
            if not isinstance(value, str) or not value.strip():
                raise LearningWriteAdmissionError(f"{field_name} must be a non-empty string")
        if not isinstance(self.domain, LearningWriteDomain):
            raise LearningWriteAdmissionError("domain must be a LearningWriteDomain member")
        if not isinstance(self.status, LearningWriteAdmissionStatus):
            raise LearningWriteAdmissionError("status must be a LearningWriteAdmissionStatus member")
        if not isinstance(self.confidence, (int, float)) or isinstance(self.confidence, bool):
            raise LearningWriteAdmissionError("confidence must be a number")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise LearningWriteAdmissionError("confidence must be between 0.0 and 1.0")
        if self.learning_write_allowed:
            raise LearningWriteAdmissionError("admission cannot grant learning-write authority")
        if self.memory_mutated:
            raise LearningWriteAdmissionError("admission cannot claim memory mutation")
        if self.authority_granted:
            raise LearningWriteAdmissionError("admission cannot grant authority")

    @property
    def admitted(self) -> bool:
        return self.status is LearningWriteAdmissionStatus.ADMITTED

    def to_context(self) -> dict[str, object]:
        return {
            "learning_write_admission_id": self.admission_id,
            "learning_write_proposal_id": self.proposal_id,
            "learning_decision_id": self.decision_id,
            "learning_candidate_id": self.candidate_id,
            "learning_write_domain": self.domain.value,
            "learning_write_admission_status": self.status.value,
            "learning_write_admitted": self.admitted,
            "learning_write_allowed": False,
            "learning_written": False,
            "memory_mutated": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
        }


class LearningWriteAdmissionProvider:
    """Provider-neutral contract for learning-write policy admission."""

    def admit(self, context: LearningWriteAdmissionContext) -> LearningWriteAdmission:
        raise NotImplementedError

    def provider_name(self) -> str:
        raise NotImplementedError


class DeterministicLearningWriteAdmissionProvider(LearningWriteAdmissionProvider):
    """Dependency-free baseline policy for structural learning-write admission."""

    _MIN_CONFIDENCE = 0.5

    def provider_name(self) -> str:
        return "deterministic"

    def admit(self, context: LearningWriteAdmissionContext) -> LearningWriteAdmission:
        if not isinstance(context, LearningWriteAdmissionContext):
            raise TypeError("context must be a LearningWriteAdmissionContext")
        proposal = context.proposal
        if not isinstance(proposal, LearningWriteProposal):
            raise TypeError("context.proposal must be a LearningWriteProposal")

        reason = self._validate_proposal(proposal)
        status = LearningWriteAdmissionStatus.REJECTED if reason else LearningWriteAdmissionStatus.ADMITTED
        return self._result(
            proposal,
            status,
            reason or "proposal satisfies the deterministic learning-write admission policy",
        )

    @classmethod
    def _validate_proposal(cls, proposal: LearningWriteProposal) -> str | None:
        if not proposal.payload:
            return "learning-write proposal payload must not be empty"
        if not proposal.evidence:
            return "learning-write proposal requires evidence"
        if not proposal.provenance:
            return "learning-write proposal requires provenance"
        if proposal.confidence < cls._MIN_CONFIDENCE:
            return "learning-write proposal confidence is below the admission threshold"
        return None

    @staticmethod
    def _result(
        proposal: LearningWriteProposal,
        status: LearningWriteAdmissionStatus,
        reason: str,
    ) -> LearningWriteAdmission:
        serialized = json.dumps(
            {
                "proposal_id": proposal.proposal_id,
                "domain": proposal.domain.value,
                "status": status.value,
                "reason": reason,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        admission_id = f"learn-write-admission-{hashlib.sha256(serialized).hexdigest()[:24]}"
        return LearningWriteAdmission(
            admission_id=admission_id,
            proposal_id=proposal.proposal_id,
            decision_id=proposal.decision_id,
            candidate_id=proposal.candidate_id,
            domain=proposal.domain,
            status=status,
            reason=reason,
            confidence=float(proposal.confidence),
            policy_id="deterministic-learning-write-v1",
        )


class LearningWriteAdmissionService:
    """Apply one replaceable learning-write admission policy."""

    def __init__(self, provider: LearningWriteAdmissionProvider | None = None) -> None:
        self._provider = provider or DeterministicLearningWriteAdmissionProvider()

    def admit(self, context: LearningWriteAdmissionContext) -> LearningWriteAdmission:
        if not isinstance(context, LearningWriteAdmissionContext):
            raise TypeError("context must be a LearningWriteAdmissionContext")
        proposal = context.proposal
        if not isinstance(proposal, LearningWriteProposal):
            raise TypeError("context.proposal must be a LearningWriteProposal")

        admission = self._provider.admit(context)
        if not isinstance(admission, LearningWriteAdmission):
            raise TypeError("learning-write admission provider must return LearningWriteAdmission")
        if admission.proposal_id != proposal.proposal_id:
            raise LearningWriteAdmissionError("admission proposal identity does not match proposal")
        if admission.decision_id != proposal.decision_id:
            raise LearningWriteAdmissionError("admission decision identity does not match proposal")
        if admission.candidate_id != proposal.candidate_id:
            raise LearningWriteAdmissionError("admission candidate identity does not match proposal")
        if admission.domain is not proposal.domain:
            raise LearningWriteAdmissionError("admission domain does not match proposal")
        return admission
