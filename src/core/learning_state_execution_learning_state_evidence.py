"""M23.164: record bounded learning-state evidence without transitioning or mutating state."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.learning_state_execution_learning_proposal_application_integrity import LearningStateExecutionLearningProposalApplicationIntegrity


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
    application_status: Any
    evidence_collector_id: str
    evidence_purpose: str
    evidence_rationale: Any
    evidence_payload: Any
    status: LearningStateExecutionLearningStateEvidenceStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        required_strings = (
            "evidence_id", "integrity_id", "application_id", "decision_id", "proposal_id", "eligibility_id",
            "source_integrity_id", "signal_id", "evaluation_id", "feedback_id", "outcome_id", "attempt_id",
            "admission_id", "eligibility_source_id", "handling_id", "consumption_id", "receipt_id", "handoff_id",
            "inherited_integrity_id", "validation_id", "semantic_use_id", "source_request_id", "source_request_lineage_id",
            "source_validation_id", "source_validation_lineage_id", "interpretation_id", "read_id", "consumption_request_id",
            "requester_id", "consumer_id", "handoff_target_id", "recipient_id", "handling_target_id", "execution_target_id",
            "signal_purpose", "learner_id", "eligibility_purpose", "proposer_id", "proposal_purpose", "decision_maker_id",
            "decision_purpose", "applier_id", "application_purpose", "evidence_collector_id", "evidence_purpose",
        )
        for name in required_strings:
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        for name in ("source_signal_fingerprint", "computed_signal_fingerprint"):
            if len(getattr(self, name)) != 64:
                raise ValueError("learning-state evidence requires SHA-256 signal fingerprints")
        if not isinstance(self.status, LearningStateExecutionLearningStateEvidenceStatus):
            raise TypeError("status must be a learning-state evidence status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "signal_context", _freeze(self.signal_context))
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
    """Record state-effect evidence without applying, transitioning, or persisting state."""

    def record(
        self,
        integrity: "LearningStateExecutionLearningProposalApplicationIntegrity",
        *,
        evidence_id: str,
        evidence_collector_id: str,
        evidence_purpose: str,
        evidence_rationale: Any,
        evidence_payload: Any,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionLearningStateEvidence:
        from src.core.learning_state_execution_learning_proposal_application_integrity import (
            LearningStateExecutionLearningProposalApplicationIntegrity,
            LearningStateExecutionLearningProposalApplicationIntegrityStatus,
        )

        if type(integrity) is not LearningStateExecutionLearningProposalApplicationIntegrity:
            raise TypeError("integrity must be a learning-proposal application integrity artifact")
        for name, value in (("evidence_id", evidence_id), ("evidence_collector_id", evidence_collector_id), ("evidence_purpose", evidence_purpose)):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if evidence_rationale is None:
            raise ValueError("evidence_rationale must be provided")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")

        anchored_integrity_id = integrity.lineage.get("integrity_id", integrity.integrity_id)
        anchored_application_id = integrity.lineage.get("application_id", integrity.application_id)
        anchored_source_integrity_id = integrity.lineage.get("source_integrity_id", integrity.source_integrity_id)
        lineage_consistent = (
            anchored_integrity_id == integrity.integrity_id
            and anchored_application_id == integrity.application_id
            and anchored_source_integrity_id == integrity.source_integrity_id
        )
        recorded = (
            integrity.status is LearningStateExecutionLearningProposalApplicationIntegrityStatus.VALID
            and integrity.is_valid
            and lineage_consistent
        )
        if reasons is not None:
            final_reasons = reasons
        elif recorded:
            final_reasons = ("application integrity is VALID",)
        else:
            final_reasons = ("application integrity lineage is not valid",)
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
            eligibility_source_id=integrity.eligibility_source_id,
            handling_id=integrity.handling_id,
            consumption_id=integrity.consumption_id,
            receipt_id=integrity.receipt_id,
            handoff_id=integrity.handoff_id,
            inherited_integrity_id=integrity.inherited_integrity_id,
            validation_id=integrity.validation_id,
            semantic_use_id=integrity.semantic_use_id,
            source_request_id=integrity.source_request_id,
            source_request_lineage_id=integrity.source_request_lineage_id,
            source_validation_id=integrity.source_validation_id,
            source_validation_lineage_id=integrity.source_validation_lineage_id,
            interpretation_id=integrity.interpretation_id,
            read_id=integrity.read_id,
            consumption_request_id=integrity.consumption_request_id,
            requester_id=integrity.requester_id,
            consumer_id=integrity.consumer_id,
            handoff_target_id=integrity.handoff_target_id,
            recipient_id=integrity.recipient_id,
            handling_target_id=integrity.handling_target_id,
            execution_target_id=integrity.execution_target_id,
            signal_kind=integrity.signal_kind,
            signal_purpose=integrity.signal_purpose,
            signal_context=integrity.signal_context,
            signal_status=integrity.signal_status,
            source_signal_fingerprint=integrity.source_signal_fingerprint,
            computed_signal_fingerprint=integrity.computed_signal_fingerprint,
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
            lineage=lineage if lineage is not None else {"evidence_id": evidence_id, "integrity_id": integrity.integrity_id, "application_id": integrity.application_id, "source_integrity_id": integrity.source_integrity_id},
        )


__all__ = [
    "LearningStateExecutionLearningStateEvidenceError",
    "LearningStateExecutionLearningStateEvidenceStatus",
    "LearningStateExecutionLearningStateEvidence",
    "LearningStateExecutionLearningStateEvidenceService",
]
