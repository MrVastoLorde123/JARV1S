"""M23.165: formulate bounded learning-state transition records without mutating durable state."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.learning_state_execution_learning_state_evidence import LearningStateExecutionLearningStateEvidence


class LearningStateExecutionLearningStateTransitionError(RuntimeError):
    """Raised when a learning-state transition artifact cannot be formed safely."""


class LearningStateExecutionLearningStateTransitionStatus(str, Enum):
    FORMULATED = "FORMULATED"
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


def _canonical(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _canonical(item) for key, item in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return sorted((_canonical(item) for item in value), key=lambda item: repr(item))
    if isinstance(value, Enum):
        return value.value
    return value


def _transition_fingerprint(
    *, transition_id: str, state_key: str, state_before: Any, state_after: Any,
    evidence_id: str, integrity_id: str, proposed_change: Any,
) -> str:
    payload = {
        "transition_id": transition_id,
        "state_key": state_key,
        "state_before": _canonical(state_before),
        "state_after": _canonical(state_after),
        "evidence_id": evidence_id,
        "integrity_id": integrity_id,
        "proposed_change": _canonical(proposed_change),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class LearningStateExecutionLearningStateTransition:
    """Immutable description of one candidate learning-state transition."""

    transition_id: str
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
    state_key: str
    state_before: Any
    state_after: Any
    transition_actor_id: str
    transition_purpose: str
    transition_rationale: Any
    transition_fingerprint: str
    status: LearningStateExecutionLearningStateTransitionStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        required_strings = (
            "transition_id", "evidence_id", "integrity_id", "application_id", "decision_id", "proposal_id", "eligibility_id",
            "source_integrity_id", "signal_id", "evaluation_id", "feedback_id", "outcome_id", "attempt_id", "admission_id",
            "eligibility_source_id", "handling_id", "consumption_id", "receipt_id", "handoff_id", "inherited_integrity_id",
            "validation_id", "semantic_use_id", "source_request_id", "source_request_lineage_id", "source_validation_id",
            "source_validation_lineage_id", "interpretation_id", "read_id", "consumption_request_id", "requester_id", "consumer_id",
            "handoff_target_id", "recipient_id", "handling_target_id", "execution_target_id", "signal_purpose", "source_signal_fingerprint",
            "computed_signal_fingerprint", "learner_id", "eligibility_purpose", "proposer_id", "proposal_purpose", "decision_maker_id",
            "decision_purpose", "applier_id", "application_purpose", "evidence_collector_id", "evidence_purpose", "state_key",
            "transition_actor_id", "transition_purpose", "transition_fingerprint",
        )
        for name in required_strings:
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        for name in ("source_signal_fingerprint", "computed_signal_fingerprint", "transition_fingerprint"):
            if len(getattr(self, name)) != 64:
                raise ValueError("learning-state transition requires SHA-256 fingerprints")
        if not isinstance(self.status, LearningStateExecutionLearningStateTransitionStatus):
            raise TypeError("status must be a learning-state transition status")
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
        object.__setattr__(self, "state_before", _freeze(self.state_before))
        object.__setattr__(self, "state_after", _freeze(self.state_after))
        object.__setattr__(self, "transition_rationale", _freeze(self.transition_rationale))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_formulated(self) -> bool:
        return self.status is LearningStateExecutionLearningStateTransitionStatus.FORMULATED

    @property
    def is_rejected(self) -> bool:
        return self.status is LearningStateExecutionLearningStateTransitionStatus.REJECTED

    @property
    def represents_transition(self) -> bool:
        return self.is_formulated

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


class LearningStateExecutionLearningStateTransitionService:
    """Form explicit candidate state transitions without applying them to durable state."""

    def formulate(
        self,
        evidence: "LearningStateExecutionLearningStateEvidence",
        *,
        transition_id: str,
        state_key: str,
        state_before: Any,
        state_after: Any,
        transition_actor_id: str,
        transition_purpose: str,
        transition_rationale: Any,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionLearningStateTransition:
        from src.core.learning_state_execution_learning_state_evidence import (
            LearningStateExecutionLearningStateEvidence,
            LearningStateExecutionLearningStateEvidenceStatus,
        )

        if type(evidence) is not LearningStateExecutionLearningStateEvidence:
            raise TypeError("evidence must be a learning-state evidence artifact")
        for name, value in (("transition_id", transition_id), ("state_key", state_key), ("transition_actor_id", transition_actor_id), ("transition_purpose", transition_purpose)):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if transition_rationale is None:
            raise ValueError("transition_rationale must be provided")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if transition_id == evidence.evidence_id or transition_id == evidence.integrity_id:
            raise ValueError("transition identity must be distinct")

        anchored_evidence_id = evidence.lineage.get("evidence_id", evidence.evidence_id)
        anchored_integrity_id = evidence.lineage.get("integrity_id", evidence.integrity_id)
        anchored_application_id = evidence.lineage.get("application_id", evidence.application_id)
        anchored_source_integrity_id = evidence.lineage.get("source_integrity_id", evidence.source_integrity_id)
        lineage_consistent = (
            anchored_evidence_id == evidence.evidence_id
            and anchored_integrity_id == evidence.integrity_id
            and anchored_application_id == evidence.application_id
            and anchored_source_integrity_id == evidence.source_integrity_id
        )
        valid = evidence.status is LearningStateExecutionLearningStateEvidenceStatus.RECORDED and evidence.records_state_evidence and lineage_consistent
        if reasons is not None:
            final_reasons = reasons
        elif evidence.status is not LearningStateExecutionLearningStateEvidenceStatus.RECORDED or not evidence.records_state_evidence:
            final_reasons = ("learning-state evidence is not recorded",)
        elif not lineage_consistent:
            final_reasons = ("learning-state evidence lineage is not valid",)
        else:
            final_reasons = ("learning-state evidence is RECORDED",)
        status = LearningStateExecutionLearningStateTransitionStatus.FORMULATED if valid else LearningStateExecutionLearningStateTransitionStatus.REJECTED
        fingerprint = _transition_fingerprint(
            transition_id=transition_id,
            state_key=state_key,
            state_before=state_before,
            state_after=state_after,
            evidence_id=evidence.evidence_id,
            integrity_id=evidence.integrity_id,
            proposed_change=evidence.proposed_change,
        )
        return LearningStateExecutionLearningStateTransition(
            transition_id=transition_id,
            evidence_id=evidence.evidence_id,
            integrity_id=evidence.integrity_id,
            application_id=evidence.application_id,
            decision_id=evidence.decision_id,
            proposal_id=evidence.proposal_id,
            eligibility_id=evidence.eligibility_id,
            source_integrity_id=evidence.source_integrity_id,
            signal_id=evidence.signal_id,
            evaluation_id=evidence.evaluation_id,
            feedback_id=evidence.feedback_id,
            outcome_id=evidence.outcome_id,
            attempt_id=evidence.attempt_id,
            admission_id=evidence.admission_id,
            eligibility_source_id=evidence.eligibility_source_id,
            handling_id=evidence.handling_id,
            consumption_id=evidence.consumption_id,
            receipt_id=evidence.receipt_id,
            handoff_id=evidence.handoff_id,
            inherited_integrity_id=evidence.inherited_integrity_id,
            validation_id=evidence.validation_id,
            semantic_use_id=evidence.semantic_use_id,
            source_request_id=evidence.source_request_id,
            source_request_lineage_id=evidence.source_request_lineage_id,
            source_validation_id=evidence.source_validation_id,
            source_validation_lineage_id=evidence.source_validation_lineage_id,
            interpretation_id=evidence.interpretation_id,
            read_id=evidence.read_id,
            consumption_request_id=evidence.consumption_request_id,
            requester_id=evidence.requester_id,
            consumer_id=evidence.consumer_id,
            handoff_target_id=evidence.handoff_target_id,
            recipient_id=evidence.recipient_id,
            handling_target_id=evidence.handling_target_id,
            execution_target_id=evidence.execution_target_id,
            signal_kind=evidence.signal_kind,
            signal_purpose=evidence.signal_purpose,
            signal_context=evidence.signal_context,
            signal_status=evidence.signal_status,
            source_signal_fingerprint=evidence.source_signal_fingerprint,
            computed_signal_fingerprint=evidence.computed_signal_fingerprint,
            learner_id=evidence.learner_id,
            eligibility_purpose=evidence.eligibility_purpose,
            proposer_id=evidence.proposer_id,
            proposal_purpose=evidence.proposal_purpose,
            proposed_change=evidence.proposed_change,
            proposal_rationale=evidence.proposal_rationale,
            decision_maker_id=evidence.decision_maker_id,
            decision_purpose=evidence.decision_purpose,
            decision_rationale=evidence.decision_rationale,
            applier_id=evidence.applier_id,
            application_purpose=evidence.application_purpose,
            application_rationale=evidence.application_rationale,
            application_evidence=evidence.application_evidence,
            application_status=evidence.application_status,
            evidence_collector_id=evidence.evidence_collector_id,
            evidence_purpose=evidence.evidence_purpose,
            evidence_rationale=evidence.evidence_rationale,
            evidence_payload=evidence.evidence_payload,
            state_key=state_key,
            state_before=state_before,
            state_after=state_after,
            transition_actor_id=transition_actor_id,
            transition_purpose=transition_purpose,
            transition_rationale=transition_rationale,
            transition_fingerprint=fingerprint,
            status=status,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {
                "transition_id": transition_id,
                "evidence_id": evidence.evidence_id,
                "integrity_id": evidence.integrity_id,
                "application_id": evidence.application_id,
                "source_integrity_id": evidence.source_integrity_id,
            },
        )


__all__ = [
    "LearningStateExecutionLearningStateTransitionError",
    "LearningStateExecutionLearningStateTransitionStatus",
    "LearningStateExecutionLearningStateTransition",
    "LearningStateExecutionLearningStateTransitionService",
]
