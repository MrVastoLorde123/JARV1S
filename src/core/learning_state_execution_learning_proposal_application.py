"""M23.162: apply one approved learning-proposal decision without granting execution or authority."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.learning_state_execution_learning_proposal_decision import LearningStateExecutionLearningProposalDecision


class LearningStateExecutionLearningProposalApplicationError(RuntimeError):
    """Raised when bounded learning-proposal application evidence cannot be formed safely."""


class LearningStateExecutionLearningProposalApplicationStatus(str, Enum):
    APPLIED = "APPLIED"
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
class LearningStateExecutionLearningProposalApplication:
    """Immutable evidence that an approved learning decision crossed the application boundary."""

    application_id: str
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
    applier_id: str
    application_purpose: str
    application_rationale: Any
    application_evidence: Any
    status: LearningStateExecutionLearningProposalApplicationStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "application_id", "decision_id", "proposal_id", "eligibility_id", "integrity_id", "signal_id",
            "evaluation_id", "feedback_id", "outcome_id", "attempt_id", "admission_id", "eligibility_source_id",
            "handling_id", "consumption_id", "receipt_id", "handoff_id", "inherited_integrity_id", "validation_id",
            "semantic_use_id", "source_request_id", "source_request_lineage_id", "source_validation_id",
            "source_validation_lineage_id", "interpretation_id", "read_id", "consumption_request_id", "requester_id",
            "consumer_id", "handoff_target_id", "recipient_id", "handling_target_id", "execution_target_id",
            "signal_purpose", "source_signal_fingerprint", "computed_signal_fingerprint", "learner_id",
            "eligibility_purpose", "proposer_id", "proposal_purpose", "decision_maker_id", "decision_purpose",
            "applier_id", "application_purpose",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        for name in ("source_signal_fingerprint", "computed_signal_fingerprint"):
            value = getattr(self, name)
            if len(value) != 64:
                raise ValueError("learning proposal application requires SHA-256 signal fingerprints")
        if not isinstance(self.status, LearningStateExecutionLearningProposalApplicationStatus):
            raise TypeError("status must be a learning-proposal application status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        if self.application_rationale is None:
            raise ValueError("application_rationale must be provided")
        object.__setattr__(self, "signal_context", _freeze(self.signal_context))
        object.__setattr__(self, "proposed_change", _freeze(self.proposed_change))
        object.__setattr__(self, "proposal_rationale", _freeze(self.proposal_rationale))
        object.__setattr__(self, "decision_rationale", _freeze(self.decision_rationale))
        object.__setattr__(self, "application_rationale", _freeze(self.application_rationale))
        object.__setattr__(self, "application_evidence", _freeze(self.application_evidence))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_applied(self) -> bool:
        return self.status is LearningStateExecutionLearningProposalApplicationStatus.APPLIED

    @property
    def is_rejected(self) -> bool:
        return self.status is LearningStateExecutionLearningProposalApplicationStatus.REJECTED

    @property
    def is_learning(self) -> bool:
        return False

    @property
    def applies_learning(self) -> bool:
        return False

    @property
    def authorizes_learning(self) -> bool:
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

    @property
    def proposes_adaptation(self) -> bool:
        return False


class LearningStateExecutionLearningProposalApplicationService:
    """Record application-boundary evidence only from an explicitly approved decision."""

    def apply(
        self,
        decision: "LearningStateExecutionLearningProposalDecision",
        *,
        application_id: str,
        applier_id: str,
        application_purpose: str,
        application_rationale: Any,
        application_evidence: Any = None,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionLearningProposalApplication:
        from src.core.learning_state_execution_learning_proposal_decision import (
            LearningStateExecutionLearningProposalDecision,
            LearningStateExecutionLearningProposalDecisionStatus,
        )

        if type(decision) is not LearningStateExecutionLearningProposalDecision:
            raise TypeError("decision must be a learning-proposal decision artifact")
        for name, value in (("application_id", application_id), ("applier_id", applier_id), ("application_purpose", application_purpose)):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if application_rationale is None:
            raise ValueError("application_rationale must be provided")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if application_id == decision.decision_id:
            raise ValueError("application identity must be distinct")

        applied = decision.status is LearningStateExecutionLearningProposalDecisionStatus.APPROVED and decision.is_approved
        final_reasons = reasons if reasons is not None else (("learning proposal decision is APPROVED",) if applied else ("learning proposal decision is not APPROVED",))
        status = LearningStateExecutionLearningProposalApplicationStatus.APPLIED if applied else LearningStateExecutionLearningProposalApplicationStatus.REJECTED

        return LearningStateExecutionLearningProposalApplication(
            application_id=application_id,
            decision_id=decision.decision_id,
            proposal_id=decision.proposal_id,
            eligibility_id=decision.eligibility_id,
            integrity_id=decision.integrity_id,
            signal_id=decision.signal_id,
            evaluation_id=decision.evaluation_id,
            feedback_id=decision.feedback_id,
            outcome_id=decision.outcome_id,
            attempt_id=decision.attempt_id,
            admission_id=decision.admission_id,
            eligibility_source_id=decision.eligibility_source_id,
            handling_id=decision.handling_id,
            consumption_id=decision.consumption_id,
            receipt_id=decision.receipt_id,
            handoff_id=decision.handoff_id,
            inherited_integrity_id=decision.inherited_integrity_id,
            validation_id=decision.validation_id,
            semantic_use_id=decision.semantic_use_id,
            source_request_id=decision.source_request_id,
            source_request_lineage_id=decision.source_request_lineage_id,
            source_validation_id=decision.source_validation_id,
            source_validation_lineage_id=decision.source_validation_lineage_id,
            interpretation_id=decision.interpretation_id,
            read_id=decision.read_id,
            consumption_request_id=decision.consumption_request_id,
            requester_id=decision.requester_id,
            consumer_id=decision.consumer_id,
            handoff_target_id=decision.handoff_target_id,
            recipient_id=decision.recipient_id,
            handling_target_id=decision.handling_target_id,
            execution_target_id=decision.execution_target_id,
            signal_kind=decision.signal_kind,
            signal_purpose=decision.signal_purpose,
            signal_context=decision.signal_context,
            signal_status=decision.signal_status,
            source_signal_fingerprint=decision.source_signal_fingerprint,
            computed_signal_fingerprint=decision.computed_signal_fingerprint,
            learner_id=decision.learner_id,
            eligibility_purpose=decision.eligibility_purpose,
            proposer_id=decision.proposer_id,
            proposal_purpose=decision.proposal_purpose,
            proposed_change=decision.proposed_change,
            proposal_rationale=decision.proposal_rationale,
            decision_maker_id=decision.decision_maker_id,
            decision_purpose=decision.decision_purpose,
            decision_rationale=decision.decision_rationale,
            applier_id=applier_id,
            application_purpose=application_purpose,
            application_rationale=application_rationale,
            application_evidence=application_evidence,
            status=status,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {"application_id": application_id, "decision_id": decision.decision_id},
        )


__all__ = [
    "LearningStateExecutionLearningProposalApplicationError",
    "LearningStateExecutionLearningProposalApplicationStatus",
    "LearningStateExecutionLearningProposalApplication",
    "LearningStateExecutionLearningProposalApplicationService",
]