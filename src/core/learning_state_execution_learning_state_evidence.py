"""M23.132: record bounded learning-state evidence without transitioning state."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_execution_learning_proposal_application_integrity import (
    LearningStateExecutionLearningProposalApplicationIntegrity,
    LearningStateExecutionLearningProposalApplicationIntegrityStatus,
)


class LearningStateExecutionLearningStateEvidenceError(RuntimeError):
    """Raised when learning-state evidence cannot be formed safely."""


class LearningStateExecutionLearningStateEvidenceStatus(str, Enum):
    RECORDED = "RECORDED"
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
class LearningStateExecutionLearningStateEvidence:
    """Immutable evidence describing a candidate learning-state effect."""

    evidence_id: str
    integrity_id: str
    application_id: str
    decision_id: str
    proposal_id: str
    eligibility_id: str
    source_integrity_id: str
    signal_id: str
    evaluation_id: str
    feedback_id: str
    outcome_id: str
    attempt_id: str
    admission_id: str
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
    signal_kind: Any
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
    application_status: Any
    evidence_collector_id: str
    evidence_purpose: str
    evidence_rationale: Any
    evidence_payload: Any
    status: LearningStateExecutionLearningStateEvidenceStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "evidence_id", "integrity_id", "application_id", "decision_id", "proposal_id", "eligibility_id",
            "source_integrity_id", "signal_id", "evaluation_id", "feedback_id", "outcome_id", "attempt_id",
            "admission_id", "validation_id", "use_id", "request_id", "interpretation_id", "source_request_id",
            "read_validation_id", "read_id", "consumption_request_id", "source_validation_id", "transition_id",
            "state_key", "transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint",
            "consumer_id", "execution_target_id", "execution_purpose", "objective", "evaluator_id", "evaluation_purpose",
            "signal_purpose", "learner_id", "eligibility_purpose", "proposer_id", "proposal_purpose", "decision_maker_id",
            "decision_purpose", "applier_id", "application_purpose", "evidence_collector_id", "evidence_purpose",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be numeric and between 0.0 and 1.0")
        if not isinstance(self.status, LearningStateExecutionLearningStateEvidenceStatus):
            raise TypeError("status must be a learning-state evidence status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        if self.status is LearningStateExecutionLearningStateEvidenceStatus.RECORDED:
            for name in ("transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint"):
                value = getattr(self, name)
                if len(value) != 64:
                    raise ValueError("learning-state evidence requires SHA-256 fingerprints")
        object.__setattr__(self, "proposed_change", _freeze(self.proposed_change))
        object.__setattr__(self, "proposal_rationale", _freeze(self.proposal_rationale))
        object.__setattr__(self, "decision_rationale", _freeze(self.decision_rationale))
        object.__setattr__(self, "application_rationale", _freeze(self.application_rationale))
        object.__setattr__(self, "application_evidence", _freeze(self.application_evidence))
        object.__setattr__(self, "evidence_rationale", _freeze(self.evidence_rationale))
        object.__setattr__(self, "evidence_payload", _freeze(self.evidence_payload))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_recorded(self) -> bool:
        return self.status is LearningStateExecutionLearningStateEvidenceStatus.RECORDED

    @property
    def is_rejected(self) -> bool:
        return self.status is LearningStateExecutionLearningStateEvidenceStatus.REJECTED

    @property
    def records_state_evidence(self) -> bool:
        return self.is_recorded

    @property
    def transitions_state(self) -> bool:
        return False

    @property
    def mutates_state(self) -> bool:
        return False

    @property
    def persists_state(self) -> bool:
        return False

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
    def invokes_executor(self) -> bool:
        return False

    @property
    def schedules_work(self) -> bool:
        return False

    @property
    def plans_work(self) -> bool:
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


class LearningStateExecutionLearningStateEvidenceService:
    """Record learning-state evidence without applying or transitioning state."""

    def record(
        self,
        integrity: LearningStateExecutionLearningProposalApplicationIntegrity,
        *,
        evidence_id: str,
        evidence_collector_id: str,
        evidence_purpose: str,
        evidence_rationale: Any,
        evidence_payload: Any,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionLearningStateEvidence:
        if type(integrity) is not LearningStateExecutionLearningProposalApplicationIntegrity:
            raise TypeError("integrity must be a learning-proposal application integrity artifact")
        for name, value in (
            ("evidence_id", evidence_id),
            ("evidence_collector_id", evidence_collector_id),
            ("evidence_purpose", evidence_purpose),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if evidence_rationale is None:
            raise ValueError("evidence_rationale must be provided")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")

        recorded = integrity.status is LearningStateExecutionLearningProposalApplicationIntegrityStatus.VALID and integrity.is_valid
        if reasons is not None:
            final_reasons = reasons
        elif recorded:
            final_reasons = ("application integrity is VALID",)
        else:
            final_reasons = ("application integrity is not VALID",)
        status = LearningStateExecutionLearningStateEvidenceStatus.RECORDED if recorded else LearningStateExecutionLearningStateEvidenceStatus.REJECTED
        return LearningStateExecutionLearningStateEvidence(
            evidence_id=evidence_id,
            integrity_id=integrity.integrity_id,
            application_id=integrity.application_id,
            decision_id=integrity.decision_id,
            proposal_id=integrity.proposal_id,
            eligibility_id=integrity.eligibility_id,
            source_integrity_id=integrity.source_integrity_id,
            signal_id=integrity.signal_id,
            evaluation_id=integrity.evaluation_id,
            feedback_id=integrity.feedback_id,
            outcome_id=integrity.outcome_id,
            attempt_id=integrity.attempt_id,
            admission_id=integrity.admission_id,
            validation_id=integrity.validation_id,
            use_id=integrity.use_id,
            request_id=integrity.request_id,
            interpretation_id=integrity.interpretation_id,
            source_request_id=integrity.source_request_id,
            read_validation_id=integrity.read_validation_id,
            read_id=integrity.read_id,
            consumption_request_id=integrity.consumption_request_id,
            source_validation_id=integrity.source_validation_id,
            transition_id=integrity.transition_id,
            state_key=integrity.state_key,
            transition_fingerprint=integrity.transition_fingerprint,
            source_application_fingerprint=integrity.source_application_fingerprint,
            computed_application_fingerprint=integrity.computed_application_fingerprint,
            confidence=integrity.confidence,
            consumer_id=integrity.consumer_id,
            execution_target_id=integrity.execution_target_id,
            execution_purpose=integrity.execution_purpose,
            objective=integrity.objective,
            evaluator_id=integrity.evaluator_id,
            evaluation_purpose=integrity.evaluation_purpose,
            signal_kind=integrity.signal_kind,
            signal_purpose=integrity.signal_purpose,
            learner_id=integrity.learner_id,
            eligibility_purpose=integrity.eligibility_purpose,
            proposer_id=integrity.proposer_id,
            proposal_purpose=integrity.proposal_purpose,
            proposed_change=integrity.proposed_change,
            proposal_rationale=integrity.proposal_rationale,
            decision_maker_id=integrity.decision_maker_id,
            decision_purpose=integrity.decision_purpose,
            decision_rationale=integrity.decision_rationale,
            applier_id=integrity.applier_id,
            application_purpose=integrity.application_purpose,
            application_rationale=integrity.application_rationale,
            application_evidence=integrity.application_evidence,
            application_status=integrity.application_status,
            evidence_collector_id=evidence_collector_id,
            evidence_purpose=evidence_purpose,
            evidence_rationale=evidence_rationale,
            evidence_payload=evidence_payload,
            status=status,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {"evidence_id": evidence_id, "integrity_id": integrity.integrity_id},
        )


__all__ = [
    "LearningStateExecutionLearningStateEvidenceError",
    "LearningStateExecutionLearningStateEvidenceStatus",
    "LearningStateExecutionLearningStateEvidence",
    "LearningStateExecutionLearningStateEvidenceService",
]
