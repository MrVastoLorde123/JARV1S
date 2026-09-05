"""M21.2 bounded proactive proposal boundary.

Transforms an eligible initiative candidate into a structured proposal for
later validation. Proposal formation is not authorization, scheduling, task
creation, notification delivery, or execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from .initiative import InitiativeCandidate, InitiativeDisposition, InitiativeEvaluation


class ProposalStatus(str, Enum):
    PROPOSED = "PROPOSED"
    NEEDS_REVIEW = "NEEDS_REVIEW"


@dataclass(frozen=True)
class InitiativeProposal:
    """Immutable recommendation derived from one eligible initiative."""

    proposal_id: str
    candidate_id: str
    trigger_id: str
    title: str
    recommendation: str
    rationale: str
    evidence_ids: tuple[str, ...] = ()
    created_at: datetime | None = None
    expires_at: datetime | None = None
    confidence: float | None = None
    bounded: bool = True
    authorization_granted: bool = False
    execution_requested: bool = False

    def __post_init__(self) -> None:
        for name in ("proposal_id", "candidate_id", "trigger_id", "title", "recommendation", "rationale"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        evidence_ids = tuple(self.evidence_ids)
        if len(set(evidence_ids)) != len(evidence_ids):
            raise ValueError("evidence_ids must be unique")
        for evidence_id in evidence_ids:
            if not isinstance(evidence_id, str) or not evidence_id.strip():
                raise ValueError("evidence ids must be non-empty strings")
        object.__setattr__(self, "evidence_ids", evidence_ids)
        for name in ("created_at", "expires_at"):
            value = getattr(self, name)
            if value is not None:
                if not isinstance(value, datetime):
                    raise TypeError(f"{name} must be None or a datetime")
                if value.tzinfo is None:
                    raise ValueError(f"{name} must be timezone-aware")
        if self.expires_at is not None and self.created_at is not None and self.expires_at < self.created_at:
            raise ValueError("expires_at cannot precede created_at")
        if self.confidence is not None:
            if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)):
                raise TypeError("confidence must be None or a number")
            if not 0.0 <= float(self.confidence) <= 1.0:
                raise ValueError("confidence must be between 0 and 1")
        for name in ("bounded", "authorization_granted", "execution_requested"):
            if not isinstance(getattr(self, name), bool):
                raise TypeError(f"{name} must be a bool")
        if not self.bounded:
            raise ValueError("initiative proposals must remain bounded")
        if self.authorization_granted:
            raise ValueError("initiative proposals cannot grant authorization")
        if self.execution_requested:
            raise ValueError("initiative proposals cannot request execution")

    def to_context(self) -> dict[str, object]:
        return {
            "proposal_id": self.proposal_id,
            "candidate_id": self.candidate_id,
            "trigger_id": self.trigger_id,
            "title": self.title,
            "recommendation": self.recommendation,
            "rationale": self.rationale,
            "evidence_ids": self.evidence_ids,
            "created_at": None if self.created_at is None else self.created_at.isoformat(),
            "expires_at": None if self.expires_at is None else self.expires_at.isoformat(),
            "confidence": self.confidence,
            "bounded": True,
            "authorization_granted": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class ProposalEvaluation:
    """Immutable result of whether a candidate may become a proposal."""

    candidate_id: str
    trigger_id: str
    status: ProposalStatus
    reason: str
    proposal: InitiativeProposal | None = None

    def __post_init__(self) -> None:
        for name in ("candidate_id", "trigger_id", "reason"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.status, ProposalStatus):
            try:
                object.__setattr__(self, "status", ProposalStatus(self.status))
            except (TypeError, ValueError) as exc:
                raise TypeError("status must be a ProposalStatus") from exc
        if self.proposal is not None:
            if not isinstance(self.proposal, InitiativeProposal):
                raise TypeError("proposal must be an InitiativeProposal")
            if self.proposal.candidate_id != self.candidate_id:
                raise ValueError("proposal/candidate identity mismatch")
            if self.proposal.trigger_id != self.trigger_id:
                raise ValueError("proposal/trigger identity mismatch")
        if self.status is ProposalStatus.PROPOSED and self.proposal is None:
            raise ValueError("PROPOSED evaluation requires a proposal")
        if self.status is ProposalStatus.NEEDS_REVIEW and self.proposal is not None:
            raise ValueError("NEEDS_REVIEW evaluation cannot contain a proposal")

    def to_context(self) -> dict[str, object]:
        return {
            "candidate_id": self.candidate_id,
            "trigger_id": self.trigger_id,
            "status": self.status.value,
            "reason": self.reason,
            "proposal": None if self.proposal is None else self.proposal.to_context(),
            "authority_granted": False,
            "execution_requested": False,
        }


def build_proposal(
    candidate: InitiativeCandidate,
    evaluation: InitiativeEvaluation,
    *,
    proposal_id: str,
    recommendation: str,
    created_at: datetime,
    confidence: float | None = None,
) -> ProposalEvaluation:
    """Form one bounded proposal only from an eligible candidate."""
    if not isinstance(candidate, InitiativeCandidate):
        raise TypeError("candidate must be an InitiativeCandidate")
    if not isinstance(evaluation, InitiativeEvaluation):
        raise TypeError("evaluation must be an InitiativeEvaluation")
    if evaluation.candidate_id != candidate.candidate_id or evaluation.trigger_id != candidate.trigger_id:
        raise ValueError("evaluation/candidate identity mismatch")
    if not isinstance(created_at, datetime) or created_at.tzinfo is None:
        raise ValueError("created_at must be timezone-aware")
    if not isinstance(recommendation, str) or not recommendation.strip():
        raise ValueError("recommendation must be a non-empty string")
    if evaluation.disposition is not InitiativeDisposition.ELIGIBLE:
        return ProposalEvaluation(
            candidate.candidate_id,
            candidate.trigger_id,
            ProposalStatus.NEEDS_REVIEW,
            f"initiative disposition {evaluation.disposition.value} does not permit proposal formation",
        )
    proposal = InitiativeProposal(
        proposal_id=proposal_id,
        candidate_id=candidate.candidate_id,
        trigger_id=candidate.trigger_id,
        title=candidate.title,
        recommendation=recommendation,
        rationale=candidate.rationale,
        evidence_ids=candidate.evidence_ids,
        created_at=created_at,
        expires_at=candidate.expires_at,
        confidence=confidence,
    )
    return ProposalEvaluation(
        candidate.candidate_id,
        candidate.trigger_id,
        ProposalStatus.PROPOSED,
        "eligible initiative candidate formed a bounded proposal",
        proposal,
    )
