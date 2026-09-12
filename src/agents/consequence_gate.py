"""Deterministic consequence eligibility derived from M29 evidence evaluation.

M30 consumes an already-evaluated claim and determines whether a named
consequence is eligible to advance. Eligibility is not authorization and this
module cannot execute tools, grant permissions, mutate policy, or invoke a
provider.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping

from src.agents.claim_evidence import ClaimEvaluation, ClaimState


class ConsequenceAction(str, Enum):
    """Deterministic disposition for one requested consequence."""

    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    REQUIRE_REVIEW = "REQUIRE_REVIEW"


class ConsequenceKind(str, Enum):
    """Named workflow consequence classes governed by M30."""

    ADVANCE_WORKFLOW = "ADVANCE_WORKFLOW"
    MARK_COMPLETED = "MARK_COMPLETED"


@dataclass(frozen=True)
class ConsequenceRequest:
    """A bounded request to determine whether a consequence may advance."""

    kind: ConsequenceKind
    consequence_id: str
    metadata: Mapping[str, object] | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.kind, ConsequenceKind):
            raise TypeError("kind must be a ConsequenceKind")
        if not isinstance(self.consequence_id, str) or not self.consequence_id.strip():
            raise ValueError("consequence_id must be a non-empty string")
        if self.metadata is not None and not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping or None")


@dataclass(frozen=True)
class ConsequenceDecision:
    """Evidence-gated eligibility decision; never an authorization grant."""

    claim_id: str
    task_id: str
    consequence: ConsequenceRequest
    action: ConsequenceAction
    reason: str
    evidence_refs: tuple[str, ...]
    verification_refs: tuple[str, ...]

    @property
    def eligible(self) -> bool:
        """Whether the consequence may proceed to a separate authority layer."""
        return self.action is ConsequenceAction.ALLOW

    @property
    def authorized(self) -> bool:
        """M30 never grants execution authority."""
        return False


class EvidenceGatedConsequencePolicy:
    """Map M29 claim states to bounded consequence eligibility."""

    _REQUIRED_VERIFICATION = {
        ConsequenceKind.ADVANCE_WORKFLOW,
        ConsequenceKind.MARK_COMPLETED,
    }

    def decide(
        self,
        evaluation: ClaimEvaluation,
        consequence: ConsequenceRequest,
    ) -> ConsequenceDecision:
        if not isinstance(evaluation, ClaimEvaluation):
            raise TypeError("evaluation must be a ClaimEvaluation")
        if not isinstance(consequence, ConsequenceRequest):
            raise TypeError("consequence must be a ConsequenceRequest")

        claim = evaluation.claim
        state = evaluation.state

        if consequence.kind in self._REQUIRED_VERIFICATION:
            if state is ClaimState.VERIFIED:
                action = ConsequenceAction.ALLOW
                reason = "required verification evidence is present"
            elif state is ClaimState.SUPPORTED:
                action = ConsequenceAction.REQUIRE_REVIEW
                reason = "supporting evidence exists but required verification is absent"
            elif state in {ClaimState.PROPOSED, ClaimState.UNKNOWN}:
                action = ConsequenceAction.BLOCK
                reason = "claim lacks sufficient evidence for this consequence"
            elif state in {ClaimState.CONTRADICTED, ClaimState.DISPUTED, ClaimState.REJECTED}:
                action = ConsequenceAction.BLOCK
                reason = f"claim state {state.value} cannot unlock this consequence"
            else:
                action = ConsequenceAction.BLOCK
                reason = f"unsupported claim state {state.value}"
        else:
            action = ConsequenceAction.BLOCK
            reason = f"no M30 policy exists for consequence kind {consequence.kind.value}"

        return ConsequenceDecision(
            claim_id=claim.claim_id,
            task_id=claim.task_id,
            consequence=consequence,
            action=action,
            reason=reason,
            evidence_refs=evaluation.evidence_refs,
            verification_refs=evaluation.verification_refs,
        )


__all__ = [
    "ConsequenceAction",
    "ConsequenceDecision",
    "ConsequenceKind",
    "ConsequenceRequest",
    "EvidenceGatedConsequencePolicy",
]
