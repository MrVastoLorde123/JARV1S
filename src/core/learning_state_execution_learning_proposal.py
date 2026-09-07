"""M23.160: construct bounded learning proposals from eligible learning evidence."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.learning_state_execution_learning_eligibility import LearningStateExecutionLearningEligibility


class LearningStateExecutionLearningProposalError(RuntimeError):
    """Raised when a bounded learning proposal cannot be formed safely."""


class LearningStateExecutionLearningProposalStatus(str, Enum):
    PROPOSED = "PROPOSED"
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
class LearningStateExecutionLearningProposal:
    """Immutable candidate learning change; proposal is not a decision or authorization."""

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
    rationale: Any
    status: LearningStateExecutionLearningProposalStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "proposal_id", "eligibility_id", "integrity_id", "signal_id", "evaluation_id", "feedback_id",
            "outcome_id", "attempt_id", "admission_id", "eligibility_source_id", "handling_id", "consumption_id",
            "receipt_id", "handoff_id", "inherited_integrity_id", "validation_id", "semantic_use_id",
            "source_request_id", "source_request_lineage_id", "source_validation_id", "source_validation_lineage_id",
            "interpretation_id", "read_id", "consumption_request_id", "requester_id", "consumer_id",
            "handoff_target_id", "recipient_id", "handling_target_id", "execution_target_id", "signal_purpose",
            "source_signal_fingerprint", "computed_signal_fingerprint", "learner_id", "eligibility_purpose",
            "proposer_id", "proposal_purpose",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if len(self.source_signal_fingerprint) != 64 or len(self.computed_signal_fingerprint) != 64:
            raise ValueError("learning proposal requires SHA-256 signal fingerprints")
        if not isinstance(self.status, LearningStateExecutionLearningProposalStatus):
            raise TypeError("status must be a learning-proposal status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "signal_context", _freeze(self.signal_context))
        object.__setattr__(self, "proposed_change", _freeze(self.proposed_change))
        object.__setattr__(self, "rationale", _freeze(self.rationale))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_proposed(self) -> bool:
        return self.status is LearningStateExecutionLearningProposalStatus.PROPOSED

    @property
    def is_rejected(self) -> bool:
        return self.status is LearningStateExecutionLearningProposalStatus.REJECTED

    @property
    def is_learning(self) -> bool:
        return False

    @property
    def decides_learning(self) -> bool:
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


class LearningStateExecutionLearningProposalService:
    """Construct a candidate learning proposal from one eligible artifact without deciding or applying it."""

    def propose(
        self,
        eligibility: "LearningStateExecutionLearningEligibility",
        *,
        proposal_id: str,
        proposer_id: str,
        proposal_purpose: str,
        proposed_change: Any,
        rationale: Any = None,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionLearningProposal:
        from src.core.learning_state_execution_learning_eligibility import (
            LearningStateExecutionLearningEligibility,
            LearningStateExecutionLearningEligibilityStatus,
        )

        if type(eligibility) is not LearningStateExecutionLearningEligibility:
            raise TypeError("eligibility must be a learning-eligibility artifact")
        for name, value in (("proposal_id", proposal_id), ("proposer_id", proposer_id), ("proposal_purpose", proposal_purpose)):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if proposed_change is None:
            raise ValueError("proposed_change must be provided")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if proposal_id == eligibility.eligibility_id:
            raise ValueError("proposal identity must be distinct")

        proposed = eligibility.status is LearningStateExecutionLearningEligibilityStatus.ELIGIBLE and eligibility.is_eligible
        final_reasons = reasons if reasons is not None else (
            ("learning eligibility is ELIGIBLE",) if proposed else ("learning eligibility is not ELIGIBLE",)
        )
        status = LearningStateExecutionLearningProposalStatus.PROPOSED if proposed else LearningStateExecutionLearningProposalStatus.REJECTED

        return LearningStateExecutionLearningProposal(
            proposal_id=proposal_id,
            eligibility_id=eligibility.eligibility_id,
            integrity_id=eligibility.integrity_id,
            signal_id=eligibility.signal_id,
            evaluation_id=eligibility.evaluation_id,
            feedback_id=eligibility.feedback_id,
            outcome_id=eligibility.outcome_id,
            attempt_id=eligibility.attempt_id,
            admission_id=eligibility.admission_id,
            eligibility_source_id=eligibility.eligibility_source_id,
            handling_id=eligibility.handling_id,
            consumption_id=eligibility.consumption_id,
            receipt_id=eligibility.receipt_id,
            handoff_id=eligibility.handoff_id,
            inherited_integrity_id=eligibility.inherited_integrity_id,
            validation_id=eligibility.validation_id,
            semantic_use_id=eligibility.semantic_use_id,
            source_request_id=eligibility.source_request_id,
            source_request_lineage_id=eligibility.source_request_lineage_id,
            source_validation_id=eligibility.source_validation_id,
            source_validation_lineage_id=eligibility.source_validation_lineage_id,
            interpretation_id=eligibility.interpretation_id,
            read_id=eligibility.read_id,
            consumption_request_id=eligibility.consumption_request_id,
            requester_id=eligibility.requester_id,
            consumer_id=eligibility.consumer_id,
            handoff_target_id=eligibility.handoff_target_id,
            recipient_id=eligibility.recipient_id,
            handling_target_id=eligibility.handling_target_id,
            execution_target_id=eligibility.execution_target_id,
            signal_kind=eligibility.signal_kind,
            signal_purpose=eligibility.signal_purpose,
            signal_context=eligibility.signal_context,
            signal_status=eligibility.signal_status,
            source_signal_fingerprint=eligibility.source_signal_fingerprint,
            computed_signal_fingerprint=eligibility.computed_signal_fingerprint,
            learner_id=eligibility.learner_id,
            eligibility_purpose=eligibility.eligibility_purpose,
            proposer_id=proposer_id,
            proposal_purpose=proposal_purpose,
            proposed_change=proposed_change,
            rationale=rationale,
            status=status,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {
                "proposal_id": proposal_id,
                "eligibility_id": eligibility.eligibility_id,
            },
        )


__all__ = [
    "LearningStateExecutionLearningProposalError",
    "LearningStateExecutionLearningProposalStatus",
    "LearningStateExecutionLearningProposal",
    "LearningStateExecutionLearningProposalService",
]
