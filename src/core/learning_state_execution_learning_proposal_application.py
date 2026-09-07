"""M23.130: record a bounded application attempt from an approved learning decision."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_execution_learning_signal import LearningStateExecutionLearningSignalKind
from src.core.learning_state_execution_learning_proposal_decision import (
    LearningStateExecutionLearningProposalDecision,
    LearningStateExecutionLearningProposalDecisionStatus,
)


class LearningStateExecutionLearningProposalApplicationError(RuntimeError):
    """Raised when a learning-proposal application attempt cannot be formed safely."""


class LearningStateExecutionLearningProposalApplicationStatus(str, Enum):
    ATTEMPTED = "ATTEMPTED"
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
    """Immutable evidence that an approved learning decision entered an application attempt."""

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
    source_integrity_id: str
    validation_id: str
    use_id: str
    request_id: str
    interpretation_id: str
    source_request_id: str
    read_validation_id: str
    read_id: str
    consumption_request_id: str
    source_validation_id: str
    transition_id: str
    evidence_id: str
    state_key: str
    transition_fingerprint: str
    source_application_fingerprint: str
    computed_application_fingerprint: str
    confidence: float
    consumer_id: str
    execution_target_id: str
    execution_purpose: str
    objective: str
    evaluator_id: str
    evaluation_purpose: str
    signal_kind: LearningStateExecutionLearningSignalKind
    signal_purpose: str
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
            "source_integrity_id", "validation_id", "use_id", "request_id", "interpretation_id", "source_request_id",
            "read_validation_id", "read_id", "consumption_request_id", "source_validation_id", "transition_id",
            "evidence_id", "state_key", "transition_fingerprint", "source_application_fingerprint",
            "computed_application_fingerprint", "consumer_id", "execution_target_id", "execution_purpose", "objective",
            "evaluator_id", "evaluation_purpose", "signal_purpose", "learner_id", "eligibility_purpose", "proposer_id",
            "proposal_purpose", "decision_maker_id", "decision_purpose", "applier_id", "application_purpose",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be numeric and between 0.0 and 1.0")
        for name in ("transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint"):
            value = getattr(self, name)
            if len(value) != 64:
                raise ValueError("learning proposal application requires SHA-256 fingerprints")
        if not isinstance(self.signal_kind, LearningStateExecutionLearningSignalKind):
            raise TypeError("signal_kind must be a learning-signal kind")
        if not isinstance(self.status, LearningStateExecutionLearningProposalApplicationStatus):
            raise TypeError("status must be a learning-proposal application status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        if self.application_rationale is None:
            raise ValueError("application_rationale must be provided")
        object.__setattr__(self, "proposed_change", _freeze(self.proposed_change))
        object.__setattr__(self, "proposal_rationale", _freeze(self.proposal_rationale))
        object.__setattr__(self, "decision_rationale", _freeze(self.decision_rationale))
        object.__setattr__(self, "application_rationale", _freeze(self.application_rationale))
        object.__setattr__(self, "application_evidence", _freeze(self.application_evidence))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_attempted(self) -> bool:
        return self.status is LearningStateExecutionLearningProposalApplicationStatus.ATTEMPTED

    @property
    def is_rejected(self) -> bool:
        return self.status is LearningStateExecutionLearningProposalApplicationStatus.REJECTED

    @property
    def is_learning(self) -> bool:
        return False

    @property
    def applies_learning(self) -> bool:
        return self.is_attempted

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
    """Record an application attempt only from an explicitly approved decision."""

    def apply(
        self,
        decision: LearningStateExecutionLearningProposalDecision,
        *,
        application_id: str,
        applier_id: str,
        application_purpose: str,
        application_rationale: Any,
        application_evidence: Any = None,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionLearningProposalApplication:
        if type(decision) is not LearningStateExecutionLearningProposalDecision:
            raise TypeError("decision must be a learning-proposal decision artifact")
        for name, value in (
            ("application_id", application_id),
            ("applier_id", applier_id),
            ("application_purpose", application_purpose),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if application_rationale is None:
            raise ValueError("application_rationale must be provided")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")

        attempted = decision.status is LearningStateExecutionLearningProposalDecisionStatus.APPROVED and decision.is_approved
        final_reasons = (
            reasons
            if reasons is not None
            else (("learning proposal decision is APPROVED",) if attempted else ("learning proposal decision is not APPROVED",))
        )
        status = (
            LearningStateExecutionLearningProposalApplicationStatus.ATTEMPTED
            if attempted
            else LearningStateExecutionLearningProposalApplicationStatus.REJECTED
        )
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
            source_integrity_id=decision.source_integrity_id,
            validation_id=decision.validation_id,
            use_id=decision.use_id,
            request_id=decision.request_id,
            interpretation_id=decision.interpretation_id,
            source_request_id=decision.source_request_id,
            read_validation_id=decision.read_validation_id,
            read_id=decision.read_id,
            consumption_request_id=decision.consumption_request_id,
            source_validation_id=decision.source_validation_id,
            transition_id=decision.transition_id,
            evidence_id=decision.evidence_id,
            state_key=decision.state_key,
            transition_fingerprint=decision.transition_fingerprint,
            source_application_fingerprint=decision.source_application_fingerprint,
            computed_application_fingerprint=decision.computed_application_fingerprint,
            confidence=decision.confidence,
            consumer_id=decision.consumer_id,
            execution_target_id=decision.execution_target_id,
            execution_purpose=decision.execution_purpose,
            objective=decision.objective,
            evaluator_id=decision.evaluator_id,
            evaluation_purpose=decision.evaluation_purpose,
            signal_kind=decision.signal_kind,
            signal_purpose=decision.signal_purpose,
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
