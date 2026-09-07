"""M23.161: decide whether one learning proposal may proceed to application without applying it."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.learning_state_execution_learning_proposal import LearningStateExecutionLearningProposal


class LearningStateExecutionLearningProposalDecisionError(RuntimeError):
    """Raised when bounded learning-proposal decision evidence cannot be formed safely."""


class LearningStateExecutionLearningProposalDecisionStatus(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze(item) for item in value)
    return value


@dataclass(frozen=True)
class LearningStateExecutionLearningProposalDecision:
    """Immutable decision evidence for one learning proposal; decision is not application or authorization."""

    decision_id: str
    proposal_id: str
    eligibility_id: str
    integrity_id: str
    signal_id: str
    evaluation_id: str
    feedback_id: str
    outcome_id: str
    attempt_id: str
    admission_id: str
    eligibility_source_id: str
    handling_id: str
    consumption_id: str
    receipt_id: str
    handoff_id: str
    inherited_integrity_id: str
    validation_id: str
    semantic_use_id: str
    source_request_id: str
    source_request_lineage_id: str
    source_validation_id: str
    source_validation_lineage_id: str
    interpretation_id: str
    read_id: str
    consumption_request_id: str
    requester_id: str
    consumer_id: str
    handoff_target_id: str
    recipient_id: str
    handling_target_id: str
    execution_target_id: str
    signal_kind: Any
    signal_purpose: str
    signal_context: Any
    signal_status: Any
    source_signal_fingerprint: str
    computed_signal_fingerprint: str
    learner_id: str
    eligibility_purpose: str
    proposer_id: str
    proposal_purpose: str
    proposed_change: Any
    proposal_rationale: Any
    decision_maker_id: str
    decision_purpose: str
    decision_rationale: Any
    status: LearningStateExecutionLearningProposalDecisionStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "decision_id", "proposal_id", "eligibility_id", "integrity_id", "signal_id", "evaluation_id",
            "feedback_id", "outcome_id", "attempt_id", "admission_id", "eligibility_source_id", "handling_id",
            "consumption_id", "receipt_id", "handoff_id", "inherited_integrity_id", "validation_id", "semantic_use_id",
            "source_request_id", "source_request_lineage_id", "source_validation_id", "source_validation_lineage_id",
            "interpretation_id", "read_id", "consumption_request_id", "requester_id", "consumer_id", "handoff_target_id",
            "recipient_id", "handling_target_id", "execution_target_id", "signal_purpose", "source_signal_fingerprint",
            "computed_signal_fingerprint", "learner_id", "eligibility_purpose", "proposer_id", "proposal_purpose",
            "decision_maker_id", "decision_purpose",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if len(self.source_signal_fingerprint) != 64 or len(self.computed_signal_fingerprint) != 64:
            raise ValueError("learning proposal decision requires SHA-256 signal fingerprints")
        if not isinstance(self.status, LearningStateExecutionLearningProposalDecisionStatus):
            raise TypeError("status must be a learning-proposal decision status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "signal_context", _freeze(self.signal_context))
        object.__setattr__(self, "proposed_change", _freeze(self.proposed_change))
        object.__setattr__(self, "proposal_rationale", _freeze(self.proposal_rationale))
        object.__setattr__(self, "decision_rationale", _freeze(self.decision_rationale))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_approved(self) -> bool:
        return self.status is LearningStateExecutionLearningProposalDecisionStatus.APPROVED

    @property
    def is_rejected(self) -> bool:
        return self.status is LearningStateExecutionLearningProposalDecisionStatus.REJECTED

    @property
    def decides_learning(self) -> bool:
        return self.is_approved

    @property
    def is_learning(self) -> bool:
        return False

    @property
    def authorizes_learning(self) -> bool:
        return False

    @property
    def applies_learning(self) -> bool:
        return False

    @property
    def proposes_adaptation(self) -> bool:
        return False

    @property
    def authorizes_execution(self) -> bool:
        return False

    @property
    def authorizes_retry(self) -> bool:
        return False

    @property
    def invokes_learner(self) -> bool:
        return False

    @property
    def updates_model(self) -> bool:
        return False

    @property
    def mutates_memory(self) -> bool:
        return False

    @property
    def mutates_policy(self) -> bool:
        return False

    @property
    def invokes_executor(self) -> bool:
        return False

    @property
    def schedules_work(self) -> bool:
        return False

    @property
    def plans_work(self) -> bool:
        return False

    @property
    def establishes_truth(self) -> bool:
        return False

    @property
    def establishes_correctness(self) -> bool:
        return False

    @property
    def establishes_certainty(self) -> bool:
        return False

    @property
    def establishes_usefulness(self) -> bool:
        return False


class LearningStateExecutionLearningProposalDecisionService:
    """Decide whether one proposed learning change may proceed to the application boundary."""

    def decide(
        self,
        proposal: "LearningStateExecutionLearningProposal",
        *,
        decision_id: str,
        decision_maker_id: str,
        decision_purpose: str,
        decision_rationale: Any,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionLearningProposalDecision:
        from src.core.learning_state_execution_learning_proposal import (
            LearningStateExecutionLearningProposal,
            LearningStateExecutionLearningProposalStatus,
        )

        if type(proposal) is not LearningStateExecutionLearningProposal:
            raise TypeError("proposal must be a learning-proposal artifact")
        for name, value in (
            ("decision_id", decision_id),
            ("decision_maker_id", decision_maker_id),
            ("decision_purpose", decision_purpose),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if decision_rationale is None:
            raise ValueError("decision_rationale must be provided")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if decision_id == proposal.proposal_id:
            raise ValueError("decision identity must be distinct")

        approved = proposal.status is LearningStateExecutionLearningProposalStatus.PROPOSED and proposal.is_proposed
        final_reasons = reasons if reasons is not None else (
            ("learning proposal is PROPOSED",) if approved else ("learning proposal is not PROPOSED",)
        )
        status = LearningStateExecutionLearningProposalDecisionStatus.APPROVED if approved else LearningStateExecutionLearningProposalDecisionStatus.REJECTED

        return LearningStateExecutionLearningProposalDecision(
            decision_id=decision_id,
            proposal_id=proposal.proposal_id,
            eligibility_id=proposal.eligibility_id,
            integrity_id=proposal.integrity_id,
            signal_id=proposal.signal_id,
            evaluation_id=proposal.evaluation_id,
            feedback_id=proposal.feedback_id,
            outcome_id=proposal.outcome_id,
            attempt_id=proposal.attempt_id,
            admission_id=proposal.admission_id,
            eligibility_source_id=proposal.eligibility_source_id,
            handling_id=proposal.handling_id,
            consumption_id=proposal.consumption_id,
            receipt_id=proposal.receipt_id,
            handoff_id=proposal.handoff_id,
            inherited_integrity_id=proposal.inherited_integrity_id,
            validation_id=proposal.validation_id,
            semantic_use_id=proposal.semantic_use_id,
            source_request_id=proposal.source_request_id,
            source_request_lineage_id=proposal.source_request_lineage_id,
            source_validation_id=proposal.source_validation_id,
            source_validation_lineage_id=proposal.source_validation_lineage_id,
            interpretation_id=proposal.interpretation_id,
            read_id=proposal.read_id,
            consumption_request_id=proposal.consumption_request_id,
            requester_id=proposal.requester_id,
            consumer_id=proposal.consumer_id,
            handoff_target_id=proposal.handoff_target_id,
            recipient_id=proposal.recipient_id,
            handling_target_id=proposal.handling_target_id,
            execution_target_id=proposal.execution_target_id,
            signal_kind=proposal.signal_kind,
            signal_purpose=proposal.signal_purpose,
            signal_context=proposal.signal_context,
            signal_status=proposal.signal_status,
            source_signal_fingerprint=proposal.source_signal_fingerprint,
            computed_signal_fingerprint=proposal.computed_signal_fingerprint,
            learner_id=proposal.learner_id,
            eligibility_purpose=proposal.eligibility_purpose,
            proposer_id=proposal.proposer_id,
            proposal_purpose=proposal.proposal_purpose,
            proposed_change=proposal.proposed_change,
            proposal_rationale=proposal.rationale,
            decision_maker_id=decision_maker_id,
            decision_purpose=decision_purpose,
            decision_rationale=decision_rationale,
            status=status,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {
                "decision_id": decision_id,
                "proposal_id": proposal.proposal_id,
            },
        )


__all__ = [
    "LearningStateExecutionLearningProposalDecisionError",
    "LearningStateExecutionLearningProposalDecisionStatus",
    "LearningStateExecutionLearningProposalDecision",
    "LearningStateExecutionLearningProposalDecisionService",
]
